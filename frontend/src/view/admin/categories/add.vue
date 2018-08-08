<template>
  <Button type="dashed" style="margin-left: 2px;" @click="showModal"><Icon type="md-add-circle" /> 创建分类
    <Modal v-model="modalVisible"
           title="创建分类"
           width="700"
           :loading="loading"
           @on-ok="handleSubmit"
           @on-cancel="cancel">
      <VerticalDivider :leftSideSpan="14" :rightSideSpan="10">
        <template slot="left-side">
          <Form ref="createForm" :model="form" :rules="rules" label-position="top">
            <FormItem label="分类名" prop="name">
              <Input v-model="form.name" placeholder="请输入分类名" clearable></Input>
            </FormItem>
            <FormItem label="分类描述" prop="description">
              <Input v-model="form.description" type="textarea" :autosize="{minRows: 2}" placeholder="请输入分类描述" clearable></Input>
            </FormItem>
            <FormItem label="显示顺序" prop="displayOrder">
              <RadioGroup v-model="form.displayOrder" type="button" @on-change="handleOrderChange">
                <Radio label="min">最前</Radio>
                <Radio label="max">最后</Radio>
                <Radio label="random">随机</Radio>
                <Radio label="custom">自定义</Radio>
              </RadioGroup>
              <InputNumber v-model="form.displayOrderInput" ref="customDisplayOrderInput" :style="{ marginLeft: '10px', display: inputVisible }" placeholder="请输入值"></InputNumber>
            </FormItem>
            <FormItem label="受保护的" prop="protected">
              <i-switch v-model="form.protected" size="large">
                <span slot="open">隐藏</span>
                <span slot="close">公开</span>
              </i-switch>
            </FormItem>
          </Form>
        </template>
        <template slot="right-side">
          <Timeline>
            <TimelineItem color="blue">
              <h2>字段描述</h2>
            </TimelineItem>
            <TimelineItem color="green">
              <h3>显示顺序:</h3>
              <p>类型为整数, 值越小显示越靠前;</p>
              <p>为空即默认显示在当前分类的最后</p>
            </TimelineItem>
            <TimelineItem color="green">
              <h3>受保护的:</h3>
              <p>设置为"隐藏"后, 会对普通用户不可见</p>
            </TimelineItem>
          </Timeline>
        </template>
      </VerticalDivider>
    </Modal>
  </Button>
</template>

<script>
import { createCategory } from '@/api/category'
import VerticalDivider from '_c/vertical-divider'
import { EventBus } from '@/libs/bus'

export default {
  name: 'AddCategory',
  components: {
    VerticalDivider
  },
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
      this.modalVisible = true
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
