// �ο��������gcc -Wall -O2 -s echoc.c -o echoc.exe
// �ļ���: echoc
// ���ߣ�ǧ������
// ����cmd����echo����Ĳ�ɫ���
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
    int no_newline = 0; // Ĭ�ϻ���
    int arg_start = 1;  // ������ʼλ��

    // ��� -n ѡ��
    if (argc > 1 && strcmp(argv[1], "-n") == 0) {
        no_newline = 1;
        arg_start = 2;
    }

    // ����Ч����ʱ��ʾ����
    if (arg_start >= argc) {
        char fname[260];
        _splitpath(argv[0], NULL, NULL, fname, NULL);
        printf("Usage: %s [-n] <��ɫ1> <�ı�1> <��ɫ2> <�ı�2>...\n", fname);
        printf("  -n    : ��ֹĩβ����\n");
        printf("ʾ��: %s 12 Hello 15 World\n", fname);
        PrintColorTable();
        return 0;
    }

    // ����������ɫ���룩
    if (arg_start + 1 >= argc) {
        SetConsoleColor(atoi(argv[arg_start]));
        return 0;
    }

    // ѭ��������ɫ+�ı���
    for (int i = arg_start; i < argc; i += 2) {
        if (i + 1 >= argc) break;
        SetConsoleColor(atoi(argv[i]));
        printf("%s", argv[i + 1]);
    }

    // ���軻��
    if (!no_newline) printf("\n");
    SetConsoleColor(15); // �ָ�Ĭ����ɫ
    return 0;
}