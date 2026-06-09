import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

class FortiScriptGenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FortiGate CLI Script Generator")
        
        # 해상도를 가로 650, 세로 750으로 조정하여 세로 여백을 알맞게 최적화
        self.root.geometry("650x750") 
        self.root.configure(bg="#2c3e50")
        
        self.root.resizable(True, True)
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure("TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Malgun Gothic", 11, "bold"))
        self.style.configure("Header.TLabel", font=("Malgun Gothic", 16, "bold"), foreground="#2c3e50", background="#ecf0f1")
        self.style.configure("TEntry", font=("Malgun Gothic", 11))
        
        self.create_widgets()

    def create_widgets(self):
        # 상단 타이틀 배너
        top_frame = tk.Frame(self.root, bg="#ecf0f1", height=60)
        top_frame.pack(fill="x", side="top")
        top_frame.pack_propagate(False)
        
        header_label = ttk.Label(top_frame, text=" 🛡️ FortiGate CLI 스크립트 생성기", style="Header.TLabel")
        header_label.pack(pady=12, padx=15, anchor="w")
        
        # 메인 컨텐츠 영역
        main_frame = tk.Frame(self.root, bg="#2c3e50", padx=25, pady=15)
        main_frame.pack(fill="both", expand=True)
        
        # 1. 구분자 입력란
        prefix_label = ttk.Label(main_frame, text="1. 구분자(Prefix) 입력")
        prefix_label.pack(anchor="w", pady=(0, 3))
        
        self.prefix_entry = ttk.Entry(main_frame, font=("Malgun Gothic", 11))
        self.prefix_entry.pack(fill="x", pady=(0, 12))
        self.prefix_entry.insert(0, "20260526_")
        
        # 2. 그룹명 입력란
        group_label = ttk.Label(main_frame, text="2. 방화벽 그룹명 입력 (선택사항 - 비워두면 그룹 미생성)")
        group_label.pack(anchor="w", pady=(0, 3))
        
        self.group_entry = ttk.Entry(main_frame, font=("Malgun Gothic", 11))
        self.group_entry.pack(fill="x", pady=(0, 12))
        
        # 3. 설명(Comment) 입력란
        comment_label = ttk.Label(main_frame, text="3. 설명(Comment) 입력 (선택사항 - 비워두면 설명 미생성)")
        comment_label.pack(anchor="w", pady=(0, 3))
        
        self.comment_entry = ttk.Entry(main_frame, font=("Malgun Gothic", 11))
        self.comment_entry.pack(fill="x", pady=(0, 15))
        
        # 4. IP 리스트 입력란
        ip_label = ttk.Label(main_frame, text="4. IP 주소 목록 입력 (한 줄에 하나씩)")
        ip_label.pack(anchor="w", pady=(0, 3))
        
        # [수정] IP 입력 목록 박스의 높이 비율 조절 (fill="both" 대신 고정 크기 및 적절한 확장 유연성 부여)
        text_frame = tk.Frame(main_frame, bg="#2c3e50")
        text_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        # height=15 설정을 주어 기존보다 컴팩트한 높이(약 70% 수준)로 고정 및 가독성 최적화
        self.ip_text = tk.Text(text_frame, font=("Consolas", 11), height=15, yscrollcommand=scrollbar.set, bd=1, relief="solid", wrap="word")
        self.ip_text.pack(fill="both", expand=True, side="left")
        scrollbar.config(command=self.ip_text.yview)
        
        # 5. 변환 및 스크립트 생성 버튼
        self.gen_button = tk.Button(
            main_frame, 
            text="CLI 스크립트 (.conf) 생성하기", 
            font=("Malgun Gothic", 13, "bold"),
            bg="#2ecc71", 
            fg="white", 
            activebackground="#27ae60", 
            activeforeground="white",
            bd=0, 
            pady=12,
            cursor="hand2",
            command=self.generate_script
        )
        self.gen_button.pack(fill="x", side="bottom")

    def generate_script(self):
        prefix = self.prefix_entry.get().strip()
        group_name = self.group_entry.get().strip()
        comment_text = self.comment_entry.get().strip()
        raw_ips = self.ip_text.get("1.0", tk.END).split("\n")
        
        if not prefix:
            messagebox.showerror("입력 오류", "구분자(Prefix)를 입력해주세요.")
            return
            
        ip_lines = [line.strip() for line in raw_ips if line.strip()]
        unique_ips = []
        for ip in ip_lines:
            if ip not in unique_ips:
                unique_ips.append(ip)
                
        if not unique_ips:
            messagebox.showerror("입력 오류", "변환할 IP 주소를 입력해주세요.")
            return
            
        current_dir = os.getcwd()
        output_dir = os.path.join(current_dir, "files")
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("폴더 오류", f"files 폴더를 생성하지 못했습니다:\n{e}")
                return
                
        safe_prefix = "".join(c for c in prefix if c.isalnum() or c in ('_', '-'))
        filename = f"forti_script_{safe_prefix or 'output'}.conf"
        file_path = os.path.join(output_dir, filename)
        
        script_lines = ["config firewall address"]
        member_names = []
        
        for ip in unique_ips:
            if "/24.49.0/24" in ip:
                ip = ip.replace("/24.49.0/24", ".49.0/24")
                
            if "/" in ip:
                subnet_ip = ip
            else:
                subnet_ip = f"{ip}/32"
                
            obj_name = f"{prefix}_{subnet_ip}"
            member_names.append(f'"{obj_name}"')
            
            script_lines.append(f'edit "{obj_name}"')
            script_lines.append(f'set subnet {subnet_ip}')
            
            if comment_text:
                script_lines.append(f'set comment "{comment_text}"')
                
            script_lines.append('next')
            
        script_lines.append('end\n')
        
        if group_name:
            script_lines.append("config firewall addrgrp")
            script_lines.append(f'    edit "{group_name}"')
            members_str = " ".join(member_names)
            script_lines.append(f'        set member {members_str}')
            script_lines.append('    next')
            script_lines.append('end\n')
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(script_lines))
            
            info_msg = f"스크립트 파일이 성공적으로 저장되었습니다!\n\n▶ 파일 확장자: .conf"
            if group_name:
                info_msg += f"\n▶ 방화벽 그룹: 생성됨 ({group_name})"
            if comment_text:
                info_msg += f"\n▶ 객체 설명(Comment): 반영됨"
            info_msg += f"\n▶ 저장 경로: {file_path}"
            
            messagebox.showinfo("생성 완료", info_msg)
        except Exception as e:
            messagebox.showerror("저장 오류", f"파일을 저장하는 중 오류가 발생했습니다:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FortiScriptGenApp(root)
    root.mainloop()