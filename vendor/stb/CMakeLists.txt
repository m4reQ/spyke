project(stb)

add_library(stb STATIC "impl.c")
target_include_directories(stb PUBLIC "include")
