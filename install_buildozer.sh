#!/bin/bash
# Save as build_apk_fixed.sh

PROJECT_DIR="/media/amirminaie/524ABA454ABA261F/MyFiles/Desktop/FlashCard/FlashCard-Dev"
cd "$PROJECT_DIR"

echo "🚀 Starting APK build process..."

# Check if Buildozer is available globally
if command -v buildozer &> /dev/null; then
    echo "✅ Buildozer found globally"
    CMD="buildozer"
elif python3 -m buildozer --version &> /dev/null; then
    echo "✅ Buildozer found in system Python"
    CMD="python3 -m buildozer"
elif [ -f "venv_linux/bin/activate" ]; then
    echo "🔄 Activating venv_linux..."
    source venv_linux/bin/activate
    
    # Check if Buildozer is in venv
    if python -m buildozer --version &> /dev/null; then
        echo "✅ Buildozer found in venv"
        CMD="python -m buildozer"
    else
        echo "📦 Installing Buildozer in venv..."
        pip install buildozer cython
        CMD="python -m buildozer"
    fi
else
    echo "❌ Buildozer not found. Installing globally..."
    pip3 install --user buildozer
    export PATH="$HOME/.local/bin:$PATH"
    CMD="buildozer"
fi

echo "🔨 Initializing Buildozer..."
$CMD init

echo "📝 Configuring for alternative NDK sources..."
# Configure buildozer to use alternative sources
configure_alternative_sources() {
    echo "🔄 Setting up alternative NDK sources..."
    
    # Create or modify buildozer.spec with alternative NDK
    if [ -f "buildozer.spec" ]; then
        # Backup original
        cp buildozer.spec buildozer.spec.backup
        
        # Use older NDK version that's more widely mirrored
        sed -i 's/android.ndk = .*/android.ndk = 23c/' buildozer.spec 2>/dev/null
        sed -i 's/android.sdk = .*/android.sdk = 30/' buildozer.spec 2>/dev/null
        
        # Add if not present
        if ! grep -q "android.ndk" buildozer.spec; then
            echo -e "\nandroid.ndk = 23c" >> buildozer.spec
            echo "android.sdk = 30" >> buildozer.spec
        fi
        
        # Add mirror settings
        if ! grep -q "p4a.mirror" buildozer.spec; then
            echo "p4a.mirror = https://github.com/kivy/python-for-android" >> buildozer.spec
        fi
    fi
}

# Function to manually download NDK from alternative sources
download_ndk_manually() {
    echo "🌐 Trying to download NDK from alternative sources..."
    
    NDK_DIR="$HOME/.buildozer/android/platform"
    mkdir -p "$NDK_DIR"
    cd "$NDK_DIR"
    
    # Remove corrupted files
    rm -f android-ndk-*.zip android-ndk-*.zip.*
    
    # Try multiple alternative sources
    NDK_SOURCES=(
        "https://github.com/android/ndk/releases/download/r23c/android-ndk-r23c-linux.zip"
        "https://dl.google.com/android/repository/android-ndk-r23c-linux.zip"
        "https://mirrors.cloud.tencent.com/android/repository/android-ndk-r23c-linux.zip"
        "https://mirrors.tuna.tsinghua.edu.cn/android/repository/android-ndk-r23c-linux.zip"
    )
    
    for source in "${NDK_SOURCES[@]}"; do
        echo "🔍 Trying: $(basename "$source")"
        if wget --tries=2 --timeout=30 --continue "$source"; then
            echo "✅ Download successful from: $(basename "$source")"
            return 0
        fi
        sleep 2
    done
    
    # Try with curl if wget fails
    for source in "${NDK_SOURCES[@]}"; do
        echo "🔍 Trying with curl: $(basename "$source")"
        if curl -L --connect-timeout 20 --retry 2 -C - -O "$source"; then
            echo "✅ Download successful from: $(basename "$source")"
            return 0
        fi
        sleep 2
    done
    
    echo "❌ All download attempts failed"
    return 1
}

# Function to use Docker as fallback
use_docker_build() {
    echo "🐳 Falling back to Docker build..."
    
    if ! command -v docker &> /dev/null; then
        echo "Installing Docker..."
        sudo apt update
        sudo apt install docker.io -y
        sudo usermod -aG docker $USER
        newgrp docker
    fi
    
    echo "Running Buildozer in Docker..."
    docker run --volume "$(pwd)":/home/user/hostcwd \
        kivy/buildozer android debug
}

# Main build process with retry logic
attempt_build() {
    local attempt=1
    local max_attempts=3
    
    while [ $attempt -le $max_attempts ]; do
        echo "🔄 Build attempt $attempt of $max_attempts..."
        
        # Configure for this attempt
        if [ $attempt -eq 2 ]; then
            echo "🛠️ Attempting manual NDK download..."
            download_ndk_manually
            cd "$PROJECT_DIR"
        elif [ $attempt -eq 3 ]; then
            echo "🔄 Switching to Docker..."
            use_docker_build
            return
        fi
        
        # Try building
        echo "🔨 Starting build..."
        if $CMD -v android debug 2>&1 | tee "build_attempt_$attempt.log"; then
            echo "✅ Build completed successfully!"
            return 0
        else
            echo "❌ Build attempt $attempt failed"
            echo "📋 Error summary:"
            tail -10 "build_attempt_$attempt.log"
            
            # Clean up for next attempt
            rm -rf .buildozer/android/platform/android-ndk*.zip
            
            attempt=$((attempt + 1))
            if [ $attempt -le $max_attempts ]; then
                echo "⏳ Waiting 5 seconds before next attempt..."
                sleep 5
            fi
        fi
    done
    
    echo "❌ All build attempts failed"
    return 1
}

# Configure alternative sources
configure_alternative_sources

# Start build with retry logic
attempt_build

# Check result
if ls bin/*.apk 1> /dev/null 2>&1; then
    echo "🎉 APK built successfully!"
    echo "📱 APK file(s):"
    ls -lh bin/*.apk
    
    # Copy to Windows desktop if in WSL
    if [ -d "/mnt/c/Users" ]; then
        WINDOWS_USER=$(ls /mnt/c/Users | grep -v 'Default\|Public\|All Users' | head -1)
        if [ -n "$WINDOWS_USER" ]; then
            cp bin/*.apk "/mnt/c/Users/$WINDOWS_USER/Desktop/" 2>/dev/null && \
            echo "📂 APK copied to Windows Desktop"
        fi
    fi
else
    echo "❌ Build failed after all attempts"
    echo "📋 Checking logs..."
    
    # Show most recent error
    latest_log=$(ls -t build_attempt_*.log 2>/dev/null | head -1)
    if [ -f "$latest_log" ]; then
        echo "Last errors from $latest_log:"
        tail -30 "$latest_log"
    fi
    
    # Suggest solutions
    echo -e "\n💡 Suggested fixes:"
    echo "1. Try using Docker: docker run --volume \"\$(pwd)\":/home/user/hostcwd kivy/buildozer android debug"
    echo "2. Download NDK manually and place in ~/.buildozer/android/platform/"
    echo "3. Use older NDK version: Change to 'android.ndk = 21e' in buildozer.spec"
fi