set(SOURCES
    AST.cpp
    Lexer.cpp
    Parser.cpp
    Preprocessor.cpp
    SyntaxHighlighter.cpp
)

serenity_lib(LibCpp cpp)
target_link_libraries(LibCpp LibC LibSyntax)
