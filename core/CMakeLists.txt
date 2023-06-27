##################################################
# Build a custom protoc plugin
set(PROTOC_PLUGIN ${PROJECT_NAME}_protoc_plugin)

gz_add_executable(${PROTOC_PLUGIN}
  generator/Generator.cc
  generator/generator_main.cc)
target_link_libraries(${PROTOC_PLUGIN}
  protobuf::libprotoc
  protobuf::libprotobuf)
target_include_directories(${PROTOC_PLUGIN} PRIVATE ${PROTOBUF_INCLUDE_DIR})
target_compile_features(${PROTOC_PLUGIN} PRIVATE ${GZ_CXX_11_FEATURES})

if (UNIX)
  target_link_libraries(${PROTOC_PLUGIN} pthread)
endif()

install(TARGETS ${PROTOC_PLUGIN} DESTINATION ${GZ_BIN_INSTALL_DIR})

##################################################
# Build core library
gz_get_libsources_and_unittests(sources gtest_sources)

gz_create_core_library(SOURCES
  src/Factory.cc
  src/MessageFactory.cc
  src/DynamicFactory.cc
)

target_link_libraries(${PROJECT_LIBRARY_TARGET_NAME}
  PUBLIC
    protobuf::libprotobuf
    gz-math${GZ_MATH_VER}::gz-math${GZ_MATH_VER}
    TINYXML2::TINYXML2
)

target_include_directories(${PROJECT_LIBRARY_TARGET_NAME}
  SYSTEM PUBLIC $<TARGET_PROPERTY:protobuf::libprotobuf,INTERFACE_INCLUDE_DIRECTORIES>)

if (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  # Disable warning in generated *.pb.cc code
  target_compile_options(${PROJECT_LIBRARY_TARGET_NAME} PRIVATE -Wno-invalid-offsetof)
endif()

##################################################
# Generate messages library to be use for command line tools
# and integration tests.
# This message library WILL NOT be installed and is not part of ABI/API
include(${PROJECT_SOURCE_DIR}/cmake/gz_msgs_string_utils.cmake)
include(${PROJECT_SOURCE_DIR}/cmake/gz_msgs_factory.cmake)
include(${PROJECT_SOURCE_DIR}/cmake/gz_msgs_generate.cmake)
include(${PROJECT_SOURCE_DIR}/cmake/gz_msgs_protoc.cmake)

file (GLOB proto_files ${PROJECT_SOURCE_DIR}/proto/gz/msgs/*.proto)

# Using the impl, rather than the extras function because we are building in-source
gz_msgs_generate_messages_impl(
  MSGS_GEN_SCRIPT
    ${PROJECT_SOURCE_DIR}/tools/gz_msgs_generate.py
  FACTORY_GEN_SCRIPT
    ${PROJECT_SOURCE_DIR}/tools/gz_msgs_generate_factory.py
  GZ_PROTOC_PLUGIN
    $<TARGET_FILE:${PROJECT_NAME}_protoc_plugin>
  INPUT_PROTOS
    ${proto_files}
  PROTO_PACKAGE
    "gz.msgs"
  PROTO_PATH
    ${PROJECT_SOURCE_DIR}/proto
  MSGS_LIB
    gz-msgs${PROJECT_VERSION_MAJOR}
  TARGET
    gz_msgs_msgs
)

add_subdirectory(include/gz/msgs)
add_subdirectory(cmd)
