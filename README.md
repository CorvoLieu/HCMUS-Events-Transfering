# HCMUS Events Transferring (Beta 0.1.0)
Bot được thiết lập bởi CakeBoy (Vì quá lười để chuyển từng events từ moodle của calendar qua :3)

Chuyển đổi các deadline và ghi chú từ lịch của moodle sang Google Calendar

## Lưu ý
Bot không sử dụng bất kỳ thông tin cá nhân của người dùng cho mục đích khác ngoài sử dụng cho công việc sao chép các events từ moodle sang Google Calendar, tất cả các hoạt động liên quan đến đăng nhập/đăng xuất các tài khoản trên mạng chỉ hoạt động chính trên tài khoản moodle và tài khoản Google riêng của người dùng tạo cho bot, hoàn toàn không bao gồm các quá trình thu thập thông tin của người dùng và tài liệu riêng tư của họ. Tôi sẽ không chịu trách nhiệm cho bất kỳ các hình thức mất/khóa tài khoản.
Xin cảm ơn.
## Hướng dẫn sử dụng
Vì chính sách an toàn của google, người dùng phải tạo một tài khoản google mới chỉ dành cho bot và bot sẽ sử dụng tài khoản này để tạo các Events trên Google Calendar
Phải sử dụng `Registry.py` để đăng ký tài khoản Google mới, không dùng các trình duyệt mặc định trên máy
#### Trước khi sử dụng lần đầu:
- Chạy `Registry.py` và tạo tài khoản Google mới, lưu ý là có thể sử dụng số điện thoại cùng với tài khoản chính.
- Vào tài khoản, tìm kiếm ngôn ngử và đổi thành tiếng Anh (English)
- Vào Google Calendar của tài khoản vừa tạo và tạo một Lịch mới (nếu muốn)
- Nhấp vào nút cài đặt của Lịch mà bot sẽ sử dụng để đăng tải các Events
- Chọn Setting and Sharing
- Kéo xuống mục `Sharing with specific people` và nhấn vào ` + Add people`
- Thêm tài khoản Google chính đang sử dụng
- Điều chỉnh quyền truy cập (Nên cho phép sửa chửa, thuận tiện cho sửa chữa các event)
- Mở `UpdateCalendar.py` và sửa chữa code:
  + `MoodleAcc` = Tài khoản moodle
  + `MoodlePas` = Password tài khoản moodle
  + `GGAcc` = Tài khoản Google dành cho bot
  + `GGPas` = Password tài khoản Google dành cho bot
  + `SelectedCalendar` = Lịch mới vừa tạo (nếu có tạo ở trên, nếu không để trống)
  + `numOfMonthTake` = Tháng bot sẽ lấy, kể cả tháng hiện tại (mặc định: 2)
- Chạy chương trình và bot sẽ tự động làm các phần còn lại

#### Cài đặt thông báo cho event:
Sử dụng allNotif để cài đặt thông báo với các giá trị:
        `<Giá trị tời gian>  <Đơn vị thời gian>`
- Giá trị tời gian: một số nguyên tùy chọn
- Đơn vị thời gian:
  + m: minutes
  + h: hours
  + d: days
  + w: weeks