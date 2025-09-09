@echo off
rem 这里是 Clink 启动时自动运行的脚本
rem 定义我的常用 Doskey 宏

doskey md5=CertUtil -hashfile $* MD5
doskey sha1=CertUtil -hashfile $* SHA1
doskey sha256=CertUtil -hashfile $* SHA256
doskey sha512=CertUtil -hashfile $* SHA512
doskey base64=powershell -Command "[convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(\"$*\"))"