// 参考编译参数gcc -Wall -O2 -s echoc.c -o echoc.exe
// 文件名: echoc
// 作者：千城真人
// 用于cmd下类echo命令的彩色输出
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>

void SetConsoleColor(WORD color) {
    SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), color);
}

void PrintColorTable() {
    for (int i = 0; i < 256; i++) {
        SetConsoleColor(i);
        printf("%3d ", i);
        if (i % 16 == 15) printf("\n");
    }
    SetConsoleColor(15);
}

int main(int argc, char **argv) {
    int no_newline = 0; // 默认换行
    int arg_start = 1;  // 参数起始位置

    // 检查 -n 选项
    if (argc > 1 && strcmp(argv[1], "-n") == 0) {
        no_newline = 1;
        arg_start = 2;
    }

    // 无有效参数时显示帮助
    if (arg_start >= argc) {
        char fname[260];
        _splitpath(argv[0], NULL, NULL, fname, NULL);
        printf("Usage: %s [-n] <颜色1> <文本1> <颜色2> <文本2>...\n", fname);
        printf("  -n    : 禁止末尾换行\n");
        printf("示例: %s 12 Hello 15 World\n", fname);
        PrintColorTable();
        return 0;
    }

    // 单参数（颜色代码）
    if (arg_start + 1 >= argc) {
        SetConsoleColor(atoi(argv[arg_start]));
        return 0;
    }

    // 循环处理颜色+文本对
    for (int i = arg_start; i < argc; i += 2) {
        if (i + 1 >= argc) break;
        SetConsoleColor(atoi(argv[i]));
        printf("%s", argv[i + 1]);
    }

    // 按需换行
    if (!no_newline) printf("\n");
    SetConsoleColor(15); // 恢复默认颜色
    return 0;
}