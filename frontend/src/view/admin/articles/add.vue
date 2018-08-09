<template>
  <Button type="dashed" style="margin-left: 2px;" @click="showModal"><Icon type="md-add-circle" /> 发表文章
    <!--<Modal v-model="modalVisible"
           title="文章发布"
           fullscreen
           :loading="loading"
           @on-ok="handleSubmit"
           @on-cancel="cancel">
    </Modal>-->
  </Button>
</template>

<script>
import { createCategory } from '@/api/category'
import { EventBus } from '@/libs/bus'

export default {
  name: 'AddArticle',
  data () {
    return {
      modalVisible: false,
      loading: true,
      inputVisible: 'none',
      form: {
        name: '',
        description: '',
        displayOrder: 'max',
        displayOrderInput: null,
        protected: false
      },
      rules: {
        name: [
          { required: true, message: '分类名不能为空', trigger: 'blur' },
          { type: 'string', max: 255, message: '分类名最多255个字符' }
        ],
        description: [
          { type: 'string', max: 255, message: '分类描述最多255个字符' }
        ]
      }
    }
  },
  methods: {
    showModal () {
      // this.modalVisible = true
      this.$router.push({
        name: 'admin_article_post'
      })
    },
    handleSubmit () {
      this.$refs.createForm.validate((valid) => {
        if (valid) {
          let params = {
            name: this.form.name,
            description: this.form.description,
            protected: this.form.protected
          }
          let displayOrder = (this.form.displayOrder === 'custom' && this.form.displayOrderInput !== null) ? this.form.displayOrderInput : null
          if (displayOrder !== null) params['display_order'] = displayOrder
          else params['display_order2'] = this.form.displayOrder
          return new Promise((resolve, reject) => {
            createCategory(params).then(res => {
              this.$Message.info('分类创建成功')
              this.modalVisible = false
              EventBus.$emit('categoryCreated')
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
                  message = '分类名已存在'
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
    },
    handleOrderChange (value) {
      if (value === 'custom') {
        this.inputVisible = 'inline-block'
        this.$refs.customDisplayOrderInput.focus()
      } else {
        this.inputVisible = 'none'
      }
    }
  },
  mounted () {
  }
}
</script>
