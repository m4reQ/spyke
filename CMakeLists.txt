cmake_minimum_required(VERSION 3.22)

project(SpykeProject LANGUAGES C VERSION 0.0.1)
set_property(GLOBAL PROPERTY LIBRARY_OUTPUT_DIRECTORY spyke)

find_package(Python COMPONENTS Development.Module REQUIRED)

add_subdirectory(vendor/cglm EXCLUDE_FROM_ALL)
add_subdirectory(vendor/glad)
add_subdirectory(vendor/stb)

set(C_STANDARD 17)

if (MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra)
endif()

Python_add_library(
    math MODULE
    "src_c/math/math.c"
    "src_c/math/vectorIter.c"
    "src_c/math/vectorUtils.c"
    "src_c/math/vector2.c"
    "src_c/math/vector3.c"
    "src_c/math/vector4.c"
    "src_c/math/matrix2.c"
    "src_c/math/matrix3.c"
    "src_c/math/matrix4.c"
    "src_c/math/viewport.c")
target_link_libraries(math PRIVATE cglm)
Python_add_library(profiling MODULE "src_c/profiling.c")
Python_add_library(input MODULE "src_c/input/input.c" "src_c/api.c" "src_c/enum.c")
Python_add_library(window MODULE "src_c/window/window.c" "src_c/window/windowSettings.c" "src_c/window/windowEvents.c" "src_c/api.c" "src_c/enum.c")
target_link_libraries(window PRIVATE glad_wgl opengl32)
Python_add_library(events MODULE "src_c/events/events.c" "src_c/api.c" "src_c/enum.c")
target_link_libraries(events PRIVATE stb)
Python_add_library(
    gl MODULE
    "src_c/graphics/gl.c"
    "src_c/graphics/buffer.c"
    "src_c/graphics/sync.c"
    "src_c/graphics/textureSpec.c"
    "src_c/graphics/textureUploadInfo.c"
    "src_c/graphics/texture.c"
    "src_c/graphics/vertexDescriptor.c"
    "src_c/graphics/vertexInput.c"
    "src_c/graphics/vertexArray.c"
    "src_c/graphics/shaderStageInfo.c"
    "src_c/graphics/shaderSpecializeInfo.c"
    "src_c/graphics/shader.c"
    "src_c/graphics/framebufferAttachment.c"
    "src_c/graphics/framebuffer.c"
    "src_c/api.c"
    "src_c/enum.c")
target_link_libraries(gl PRIVATE glad_gl)

install(
    TARGETS input events math
    DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist/spyke)
install(
    TARGETS profiling
    DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist/spyke/debug)
install(
    TARGETS window gl
    DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist/spyke/graphics)
install(DIRECTORY src_py/ DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist/spyke PATTERN "**/__pycache__" EXCLUDE)
install(DIRECTORY data DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist/spyke)
