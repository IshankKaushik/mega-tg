#!/usr/bin/env python3
"""
Setup script for Mega Link Downloader Bot - Updated Version
This script helps users set up the bot quickly and easily.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        Mega Link Downloader Bot - Updated Version           ║
║                     Setup Script                            ║
║                                                              ║
║              Redis-Free • File-Based • Modern               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check system dependencies"""
    print("\n🔍 Checking system dependencies...")
    
    dependencies = {
        'ffmpeg': 'FFmpeg (for video processing)',
        'mega-get': 'MEGAcmd (for downloading)',
        'megadl': 'megatools (alternative downloader)'
    }
    
    missing = []
    for cmd, desc in dependencies.items():
        if shutil.which(cmd):
            print(f"✅ {desc}")
        else:
            print(f"⚠️  {desc} - Not found")
            missing.append(cmd)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("   The bot will still work but some features may be limited.")
        print("   Please install them manually for full functionality.")

def install_python_packages():
    """Install Python packages"""
    print("\n📦 Installing Python packages...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Python packages installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python packages!")
        print("   Please run: pip install -r requirements.txt")
        return False
    return True

def create_config():
    """Create configuration file"""
    print("\n⚙️  Setting up configuration...")
    
    if os.path.exists('config.py'):
        response = input("   config.py already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("   Keeping existing config.py")
            return True
    
    try:
        shutil.copy('sample_config.py', 'config.py')
        print("✅ Created config.py from sample_config.py")
        print("   Please edit config.py with your bot credentials!")
        return True
    except Exception as e:
        print(f"❌ Failed to create config.py: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        'data',
        'logs', 
        'backup',
        'DOWNLOADS',
        'ADOWNLOADS', 
        'CREDENTIALS'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/")

def show_next_steps():
    """Show next steps to user"""
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    
    print("\n📝 Next steps:")
    print("1. Edit config.py with your bot credentials:")
    print("   - TG_BOT_TOKEN (from @BotFather)")
    print("   - APP_ID and API_HASH (from my.telegram.org)")
    print("   - OWNER_ID (your Telegram user ID)")
    
    print("\n2. Run the bot:")
    print("   python bot.py")
    
    print("\n3. Optional - Install system dependencies:")
    print("   - FFmpeg: https://ffmpeg.org/download.html")
    print("   - MEGAcmd: https://mega.nz/cmd")
    print("   - megatools: https://megatools.megous.com/")
    
    print("\n📚 Documentation:")
    print("   - README.md - Full documentation")
    print("   - CHANGELOG.md - What's new in this version")
    
    print("\n🐳 Docker deployment:")
    print("   docker-compose up -d")
    
    print("\n" + "="*60)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Check system dependencies
    check_dependencies()
    
    # Install Python packages
    if not install_python_packages():
        print("\n❌ Setup failed at package installation!")
        sys.exit(1)
    
    # Create config file
    if not create_config():
        print("\n❌ Setup failed at configuration!")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
