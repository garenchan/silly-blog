# issues

## frontend-related

1. iview-admin的tag会使用local storage进行存储, 如果另一个用户登录, 特别是权限有变化时, 之前的tag不应该全部被恢复

2. select多选框的清除某个选项后后续输入无法触发remote搜索事件或者再次输入导致选项被清空

## backend-related

1. 在配置文件中设置flask的DEBUG模式是不起作用的，只能通过环境变量FLASK_DEBUG来设置

2. MAX_CONTENT_LENGTH配置选项只对提交的表单起作用，而且只是通过与头部Content-Length进行了简单比较，没有在IO层面进行校验
