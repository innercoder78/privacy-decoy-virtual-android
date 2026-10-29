cmake_minimum_required(VERSION 3.22.1)
project(pdva_substrate C)
add_library(substrate SHARED probe.c launch.c)
target_compile_features(substrate PRIVATE c_std_11)
target_compile_options(substrate PRIVATE -Wall -Wextra -Werror -fstack-protector-strong)
# Keep full debug information, with stable identities for source and build paths.
target_compile_options(substrate PRIVATE
    "-fdebug-prefix-map=${CMAKE_CURRENT_SOURCE_DIR}=/pdva/jni/src"
    "-fdebug-prefix-map=${CMAKE_CURRENT_BINARY_DIR}=/pdva/jni/build")
target_link_options(substrate PRIVATE -Wl,-z,relro,-z,now)
