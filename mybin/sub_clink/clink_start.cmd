@echo off
rem ������ Clink ����ʱ�Զ����еĽű�
rem �����ҵĳ��� Doskey ��

doskey md5=CertUtil -hashfile $* MD5
doskey sha1=CertUtil -hashfile $* SHA1
doskey sha256=CertUtil -hashfile $* SHA256
doskey sha512=CertUtil -hashfile $* SHA512
doskey base64=powershell -Command "[convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(\"$*\"))"