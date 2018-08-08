<template>
  <Button type="dashed" style="margin-left: 2px;" @click="showModal"><Icon type="md-add-circle" /> 创建标签
    <Modal v-model="modalVisible"
            title="创建标签"
            :loading="loading"
            @on-ok="handleSubmit"
            @on-cancel="cancel">
      <Form ref="createForm" :model="form" :rules="rules" label-position="left" :label-width="80" @submit.native.prevent>
        <FormItem label="标签名" prop="name">
            <Input v-model="form.name" placeholder="请输入标签名"></Input>
        </FormItem>
      </Form>
    </Modal>
  </Button>
</template>

<script>
import { createTag } from '@/api/tag'
import { EventBus } from '@/libs/bus'
export default {
  name: 'AddTag',
  data () {
    return {
      modalVisible: false,
      loading: true,
      form: {
        name: ''
      },
      rules: {
        name: [
          { required: true, message: '标签名不能为空', trigger: 'blur' },
          { type: 'string', max: 64, message: '标签名最多64个字符' }
        ]
      }
    }
  },
  methods: {
    showModal () {
      this.modalVisible = true
    },
    handleSubmit () {
      this.$refs.createForm.validate((valid) => {
        if (valid) {
          return new Promise((resolve, reject) => {
            createTag(this.form.name).then(res => {
              this.$Message.info('标签创建成功')
              this.modalVisible = false
              EventBus.$emit('tagCreated')
              resolve()
            }).catch(err => {
              this.loading = false
              this.$nextTick(() => {
                this.loading = true
              })
              const response = err.response
              const data = response.data
              if (response.status === 409) {
                this.$Message.error('标签已存在')
              } else {
                this.$Message.error(data.error.message)
              }
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
  }
}
</script>
