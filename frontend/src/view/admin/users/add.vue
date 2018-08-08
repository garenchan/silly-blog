<template>
  <Button type="dashed" style="margin-left: 2px;" @click="showModal"><Icon type="md-add-circle" /> 创建用户
    <Modal v-model="modalVisible"
            title="创建用户"
            :loading="loading"
            @on-ok="handleSubmit"
            @on-cancel="cancel">
      <Form ref="createForm" :model="form" :rules="rules" label-position="top">
        <FormItem label="用户名" prop="name">
          <Input v-model="form.name" placeholder="请输入用户名"></Input>
        </FormItem>
        <FormItem label="昵称" prop="displayName">
          <Input v-model="form.displayName" placeholder="请输入昵称"></Input>
        </FormItem>
        <FormItem label="邮箱" prop="email">
          <Input v-model="form.email" placeholder="请输入邮箱"></Input>
        </FormItem>
        <FormItem label="密码" prop="password">
          <Input type="password" v-model="form.password" placeholder="请输入密码"></Input>
        </FormItem>
        <FormItem label="确认密码" prop="confirmPassword">
          <Input type="password" v-model="form.confirmPassword" placeholder="请输入确认密码"></Input>
        </FormItem>
        <FormItem label="角色" prop="roleId">
          <Select v-model="form.roleId" filterable>
              <Option v-for="item in roles" :value="item.id" :key="item.id">{{ item.name }}</Option>
          </Select>
        </FormItem>
      </Form>
    </Modal>
  </Button>
</template>

<script>
import { listRoles } from '@/api/role'
import { createUser } from '@/api/user'
import { EventBus } from '@/libs/bus'

export default {
  name: 'AddUser',
  data () {
    const validatePassCheck = (rule, value, callback) => {
      if (value !== this.form.password) {
        callback(new Error('确认密码与密码不一致'))
      } else {
        callback()
      }
    }

    return {
      modalVisible: false,
      loading: true,
      roles: [],
      form: {
        name: '',
        displayName: '',
        email: '',
        password: '',
        confirmPassword: '',
        roleId: null
      },
      rules: {
        name: [
          { required: true, message: '用户名不能为空', trigger: 'blur' },
          { type: 'string', min: 5, max: 64, message: '用户名最少5个字符最多255个字符' }
        ],
        email: [
          { type: 'email', message: '邮箱格式不合法', trigger: 'blur' },
          { type: 'string', max: 255, message: '邮箱最多255个字符' }
        ],
        password: [
          { required: true, message: '密码不能为空', trigger: 'blur' },
          { type: 'string', min: 6, max: 64, message: '密码最少6个字符最多64个字符' }
        ],
        confirmPassword: [
          { required: true, message: '确认密码不能为空', trigger: 'blur' },
          { validator: validatePassCheck, trigger: 'blur' }
        ],
        roleId: [
          { required: true, message: '角色不能为空', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    getRoles () {
      return new Promise((resolve, reject) => {
        listRoles().then(res => {
          this.roles = res.roles
          let defaultRole = res.roles.find(item => item.name.toLowerCase() === 'user')
          if (defaultRole) this.form.roleId = defaultRole.id
          resolve()
        }).catch(err => {
          const response = err.response
          const data = response.data
          this.$Message.error(data.error.message)
        })
      })
    },
    showModal () {
      this.modalVisible = true
    },
    handleSubmit () {
      this.$refs.createForm.validate((valid) => {
        if (valid) {
          let params = {
            name: this.form.name,
            password: this.form.password,
            roleId: this.form.roleId,
            // extras
            display_name: this.form.displayName,
            email: this.form.email
          }
          return new Promise((resolve, reject) => {
            createUser(params).then(res => {
              this.$Message.info('用户创建成功')
              this.modalVisible = false
              EventBus.$emit('userCreated')
              resolve()
            }).catch(err => {
              this.loading = false
              this.$nextTick(() => {
                this.loading = true
              })
              const response = err.response
              const data = response.data
              let message = data.error.message
              if (response.status === 409) {
                if (message.includes('name')) {
                  message = '用户名已存在'
                } else if (message.includes('email')) {
                  message = '邮箱已存在'
                }
              }
              this.$Message.error(message)
            })
          })
        } else {
          this.loading = false
          this.$nextTick(() => {
            this.loading = true
          })
        }
      })
    },
    cancel () {
      // maybe do something like reset here
    }
  },
  mounted () {
    this.getRoles()
  }
}
</script>
