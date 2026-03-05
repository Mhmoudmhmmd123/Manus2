import os, subprocess, time
from config import Config

class VideoCompressor:
    def __init__(self): self.ff = Config.FFMPEG_PATH

    def duration(self, p):
        try:
            r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",p], capture_output=True, text=True, timeout=30)
            return float(r.stdout.strip())
        except: return 0

    def compress(self, inp, preset="medium", target_mb=None):
        if not os.path.exists(inp): return {"success": False, "error": "no file"}
        name = os.path.splitext(os.path.basename(inp))[0]
        out = os.path.join(Config.COMPRESSED_DIR, f"{name}_c.mp4")
        st = Config.COMPRESSION_PRESETS.get(preset, Config.COMPRESSION_PRESETS["medium"])
        cmd = [self.ff, "-y", "-i", inp, "-c:v", "libx264", "-crf", str(st["crf"]), "-preset", st["preset"],
               "-vf", f"scale={st['resolution']}:force_original_aspect_ratio=decrease",
               "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", "-threads", "0", out]
        if target_mb:
            d = self.duration(inp)
            if d > 0:
                vbr = max(int((target_mb*8*1024)/d - 96), 200)
                cmd = [self.ff, "-y", "-i", inp, "-c:v", "libx264", "-b:v", f"{vbr}k", "-preset", st["preset"],
                       "-vf", f"scale={st['resolution']}:force_original_aspect_ratio=decrease",
                       "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", out]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            if p.returncode != 0: return {"success": False, "error": p.stderr[-200:]}
            return {"success": True, "output": out, "output_mb": os.path.getsize(out)/(1024*1024), "input_mb": os.path.getsize(inp)/(1024*1024)}
        except Exception as e: return {"success": False, "error": str(e)}

    def compress_for_wa(self, inp, max_mb=None):
        if max_mb is None: max_mb = Config.MAX_FILE_SIZE_MB
        inp_mb = os.path.getsize(inp)/(1024*1024)
        if inp_mb <= max_mb: return {"success": True, "output": inp, "compressed": False, "output_mb": inp_mb}
        ratio = max_mb / inp_mb
        if ratio > 0.7: preset = "high"
        elif ratio > 0.4: preset = "medium"
        elif ratio > 0.2: preset = "low"
        else: preset = "ultra_low"
        result = self.compress(inp, preset=preset, target_mb=max_mb*0.9)
        if result["success"]:
            result["compressed"] = True
            if result["output_mb"] > max_mb: return self.split(result["output"], max_mb)
        return result

    def split(self, inp, max_mb):
        d = self.duration(inp); fmb = os.path.getsize(inp)/(1024*1024)
        n = int(fmb/max_mb)+1; pd = d/n
        name = os.path.splitext(os.path.basename(inp))[0]; parts = []
        for i in range(n):
            out = os.path.join(Config.COMPRESSED_DIR, f"{name}_p{i+1}.mp4")
            subprocess.run([self.ff,"-y","-i",inp,"-ss",str(i*pd),"-t",str(pd),"-c","copy",out], capture_output=True, timeout=300)
            if os.path.exists(out): parts.append({"path": out, "part": i+1, "size_mb": os.path.getsize(out)/(1024*1024)})
        return {"success": True, "split": True, "parts": parts, "total_parts": len(parts)}