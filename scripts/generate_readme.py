def generate_readme(user, repos, events):
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d %H:%M UTC")
    
    project_block = build_projects(repos)
    activity_block = build_activity(events)

    return f"""<!-- AUTOMATED SYNC @ {ts} -->

<div align="center">
  <!-- ANIMATED TYPING SVG HEADER -->
  <a href="https://github.com/piyushCodes7">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=32&duration=3000&pause=1000&color=3B82F6&center=true&vCenter=true&width=700&height=70&lines=PIYUSH+SHARMA;BACKEND+ENGINEER;AI%2FML+ARCHITECT;BUILDING+SCALABLE+SYSTEMS" alt="Typing Header" />
  </a>

  <p align="center">
    <b>BE CSE (AI/ML) @ Chitkara University</b> • <b>CGPA: 9.6</b>
  </p>

  <!-- MODERN GLOWING BADGES -->
  <p align="center">
    <a href="https://linkedin.com/in/piyushCodes7"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"/></a>
    <a href="mailto:sharmapiyush74860@gmail.com"><img src="https://img.shields.io/badge/Email-EA4335?style=for-the-badge&logo=gmail&logoColor=white"/></a>
    <a href="https://leetcode.com/piyushCodes7"><img src="https://img.shields.io/badge/LeetCode-FFA116?style=for-the-badge&logo=leetcode&logoColor=black"/></a>
  </p>
</div>

<br/>

### 🛠️ Tech Stack & Systems Arsenal

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,cpp,js,fastapi,flask,mysql,docker,git,linux,postman,github,vscode&theme=dark" alt="Tech Stack Icons" />
</p>

---

### 🚀 Highlighted Engineering Systems

{project_block}

---

### ⚡ Real-Time Telemetry & Stats

<div align="center">
  <br/>
  <img src="https://github-readme-streak-stats.herokuapp.com/?user=piyushCodes7&theme=tokyonight&hide_border=true&border_radius=8" width="48%" alt="Streak Stat" />
  <img src="https://github-readme-stats.vercel.app/api?username=piyushCodes7&show_icons=true&theme=tokyonight&hide_border=true&rank_icon=github" width="48%" alt="GitHub Stats" />
  <br/><br/>
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=piyushCodes7&layout=compact&theme=tokyonight&hide_border=true" width="60%" alt="Top Languages" />
</div>

---

### 📈 Contribution Matrix

<div align="center">
  <br/>
  <img src="https://ghchart.rshah.org/3B82F6/piyushCodes7" alt="Piyush's Github Contributions" width="100%" />
</div>

---

### ⚡ Live Activity Stream

{activity_block}

<br/>
<div align="center">
  <sub>🤖 <i>Auto-updated every 6 hours via GitHub Actions • Last Sync: {ts}</i></sub>
</div>
"""