cmake_minimum_required(VERSION 3.22)

project(SpykeProject LANGUAGES C VERSION 0.0.1)
set_property(GLOBAL PROPERTY LIBRARY_OUTPUT_DIRECTORY spyke)

find_package(Python COMPONENTS Development.Module REQUIRED)

add_subdirectory(vendor/cglm EXCLUDE_FROM_ALL)

set(C_STANDARD 17)

if (MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra)
endif()

add_library(glad SHARED "vendor/glad/src/gl.c" "vendor/glad/src/wgl.c")
target_link_libraries(glad PUBLIC "opengl32")
target_include_directories(glad PUBLIC "vendor/glad/include")
target_compile_definitions(glad PUBLIC GLAD_API_CALL_EXPORT PRIVATE GLAD_API_CALL_EXPORT_BUILD)

add_library(stb STATIC "vendor/stb/impl.c")
target_include_directories(stb PUBLIC "vendor/stb")

Python_add_library(math MODULE "src_c/math/spyke_math.c" "src_c/api.c")
Python_add_library(profiling MODULE "src_c/profiling.c")
Python_add_library(input MODULE "src_c/input/input.c" "src_c/api.c" "src_c/enum.c")
Python_add_library(window MODULE "src_c/window/window.c" "src_c/window/windowSettings.c" "src_c/window/windowEvents.c" "src_c/api.c" "src_c/enum.c")
target_link_libraries(window PRIVATE glad)
Python_add_library(events MODULE "src_c/events/events.c" "src_c/api.c" "src_c/enum.c")
target_link_libraries(events PRIVATE stb)

install(
    TARGETS glad
    RUNTIME DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist/spyke)
install(
    TARGETS input events math
    DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist/spyke)
install(
    TARGETS profiling
    DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist/spyke/debug)
install(
    TARGETS window
    DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist/spyke/graphics)
install(DIRECTORY src_py/ DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist/spyke PATTERN "**/__pycache__" EXCLUDE)
install(DIRECTORY data DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist/spyke)
