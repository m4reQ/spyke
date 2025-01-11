# activate venv
./.venv/scripts/activate

# install pygl
# $pyglBuildType = "RelWithDebInfo"
$pyglBuildType = "Release"

if (Test-Path -LiteralPath "./pygl/build") {
    Remove-Item -LiteralPath "./pygl/build" -Force -Recurse
}

cmake -S ./pygl -B ./pygl/build/cmake -DCMAKE_BUILD_TYPE=$pyglBuildType
cmake --build ./pygl/build/cmake --config $pyglBuildType

$env:PYGL_BUILD_TYPE=$pyglBuildType

# no relative modules support
cd pygl
$whlFilepath = py -m easywheel -S . -B ./build
cd ..

pip install -v "./pygl/${whlFilepath}" --force-reinstall

# install pyimgui
# pip install -v ./pyimgui --force-reinstall
