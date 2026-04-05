# build.py
import os
import sys
import shutil
import subprocess


def clean():
    folders = ['build', 'dist']
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"✅ 已删除 {folder}")

    spec_file = 'CyberpunkDGLab.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"✅ 已删除 {spec_file}")


def build():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 检查图标文件
    icon_path = os.path.join(current_dir, 'software_icon.ico')
    if os.path.exists(icon_path):
        icon_arg = ['--icon=software_icon.ico']
    else:
        icon_arg = []
        print("⚠️ 警告: 找不到 software_icon.ico，将使用默认图标")

    # PyInstaller 命令（去掉 version.txt）
    cmd = [
              sys.executable, '-m', 'PyInstaller',
              '--name=CyberpunkDGLab',
              '--windowed',
              '--onefile',
              '--add-data=main_window.ui;.',
              '--add-data=config.py;.',
              '--hidden-import=pydglab_ws',
              '--hidden-import=qrcode',
              '--hidden-import=PIL',
              '--hidden-import=asyncio',
              '--collect-all=pydglab_ws',
          ] + icon_arg + ['main.py']

    print("\n📦 开始打包...")
    print("=" * 50)
    print(" ".join(cmd))
    print("=" * 50)
    result = subprocess.run(cmd)

    if result.returncode == 0:
        exe_path = os.path.join(current_dir, 'dist', 'CyberpunkDGLab.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / 1024 / 1024
            print("\n" + "=" * 50)
            print("✅ 打包完成！")
            print(f"📁 exe 位置: {exe_path}")

            print(f"📏 文件大小: {size_mb:.1f} MB")
        else:
            print("\n❌ 打包失败，请检查错误信息")
    else:
        print("\n❌ 打包失败，请检查错误信息")


if __name__ == "__main__":
    clean()
    build()
    input("\n按回车键退出...")