project(glad)

add_library(glad_gl STATIC "src/gl.c")
target_include_directories(glad_gl PUBLIC "include")

add_library(glad_wgl STATIC "src/wgl.c")
target_include_directories(glad_wgl PUBLIC "include")
