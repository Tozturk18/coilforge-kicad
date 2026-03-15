cmake_minimum_required(VERSION 3.20)

project(coilforge
    VERSION 0.1.0
    DESCRIPTION "CoilForge KiCad native engine"
    LANGUAGES C
)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# --------------------------------
# Platform-specific plugin bin dir
# --------------------------------
if(APPLE)
    set(COILFORGE_PLUGIN_PLATFORM_DIR macOS)
elseif(WIN32)
    set(COILFORGE_PLUGIN_PLATFORM_DIR Windows)
elseif(UNIX)
    set(COILFORGE_PLUGIN_PLATFORM_DIR Linux)
else()
    set(COILFORGE_PLUGIN_PLATFORM_DIR unknown)
endif()

set(COILFORGE_PLUGIN_BIN_DIR
    "${CMAKE_CURRENT_SOURCE_DIR}/plugin/plugins/bin/${COILFORGE_PLUGIN_PLATFORM_DIR}"
)

file(MAKE_DIRECTORY "${COILFORGE_PLUGIN_BIN_DIR}")

# -----------------------------
# Sources
# -----------------------------
set(COILFORGE_API_SOURCES
    engine/api/coilforge_api.c
    engine/coil/coil/coil.c
    engine/geometry/spiral/spiral.c
    engine/geometry/vec2/vec2.c
)

set(COILFORGE_API_HEADERS
    engine/api/coilforge_api.h
    engine/coil/coil/coil.h
    engine/geometry/spiral/spiral.h
    engine/geometry/vec2/vec2.h
)

# -----------------------------
# Shared library for ctypes
# -----------------------------
add_library(coilforge SHARED
    ${COILFORGE_API_SOURCES}
    ${COILFORGE_API_HEADERS}
)

target_compile_definitions(coilforge
    PRIVATE
        COILFORGE_BUILD_DLL
)

target_include_directories(coilforge
    PUBLIC
        "${CMAKE_CURRENT_SOURCE_DIR}/engine/api"
        "${CMAKE_CURRENT_SOURCE_DIR}/engine/coil/coil"
        "${CMAKE_CURRENT_SOURCE_DIR}/engine/geometry/spiral"
        "${CMAKE_CURRENT_SOURCE_DIR}/engine/geometry/vec2"
)

target_compile_options(coilforge
    PRIVATE
        -Wall
        -Wextra
        -Wpedantic
)

set_target_properties(coilforge PROPERTIES
    OUTPUT_NAME "coilforge"
    LIBRARY_OUTPUT_DIRECTORY "${COILFORGE_PLUGIN_BIN_DIR}"
    RUNTIME_OUTPUT_DIRECTORY "${COILFORGE_PLUGIN_BIN_DIR}"
    ARCHIVE_OUTPUT_DIRECTORY "${COILFORGE_PLUGIN_BIN_DIR}"
)

# Keep outputs out of per-config subfolders on multi-config generators.
foreach(CONFIG_TYPE ${CMAKE_CONFIGURATION_TYPES})
    string(TOUPPER "${CONFIG_TYPE}" CONFIG_UPPER)
    set_target_properties(coilforge PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY_${CONFIG_UPPER} "${COILFORGE_PLUGIN_BIN_DIR}"
        RUNTIME_OUTPUT_DIRECTORY_${CONFIG_UPPER} "${COILFORGE_PLUGIN_BIN_DIR}"
        ARCHIVE_OUTPUT_DIRECTORY_${CONFIG_UPPER} "${COILFORGE_PLUGIN_BIN_DIR}"
    )
endforeach()

# -----------------------------
# Optional CLI test executable
# -----------------------------
add_executable(coilforge_cli
    main/main.c
)

target_include_directories(coilforge_cli
    PRIVATE
        "${CMAKE_CURRENT_SOURCE_DIR}/engine/api"
        "${CMAKE_CURRENT_SOURCE_DIR}/engine/coil/coil"
        "${CMAKE_CURRENT_SOURCE_DIR}/engine/geometry/spiral"
        "${CMAKE_CURRENT_SOURCE_DIR}/engine/geometry/vec2"
)

target_link_libraries(coilforge_cli
    PRIVATE
        coilforge
)

target_compile_options(coilforge_cli
    PRIVATE
        -Wall
        -Wextra
        -Wpedantic
)
