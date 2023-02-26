# Builds the cloudfunction package
# Usage: ./build.sh

# Download the zip tool if it doesn't exist
if [ ! -f /usr/bin/zip ]; then
    echo "Installing zip"
    sudo apt-get install zip
fi
# Creates the /build directory if it doesn't exist
mkdir -p build
# Navigate to the source code directory
cd src/processor_function
# Zip
zip -r ../../build/processor_function.zip .