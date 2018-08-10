<template>
  <div>
    <Card>
      <Form ref="postForm" :model="form" :rules="rules" :label-width="80">
        <Row>
          <Col span="18">
            <FormItem label="文章标题" prop="title">
              <Input v-model="form.title" placeholder="请输入文章标题"/>
            </FormItem>
            <FormItem label="文章摘要">
              <Input v-model="form.summary" type="textarea" placeholder="请输入文章摘要"/>
            </FormItem>
            <FormItem label="文章内容" prop="content">
              <markdown-editor v-model="form.content"/>
            </FormItem>
          </Col>
          <Col span="6">
            <FormItem label="文章来源" prop="sourceId">
              <Select v-model="form.sourceId" placeholder="请选择文章来源">
                <Option v-for="item in sources" :value="item.id" :key="item.id">{{ item.name }}</Option>
              </Select>
            </FormItem>
            <FormItem label="文章分类" prop="categoryId">
              <Cascader v-model="form.categoryId"
                        :data="categories"
                        :load-data="loadSubCategories"
                        :render-format="categoryFormat"
                        filterable
                        placeholder="请选择文章分类"/>
            </FormItem>
            <FormItem label="文章标签" prop="tag">
              <Select v-model="form.tags"
                      multiple filterable
                      remote :remote-method="tagRemoteSearch"
                      :loading="tagLoading"
                      :not-found-text="tagNotFoundText"
                      @on-change="onTagSelectChange"
                      placeholder="最多可选5个标签">
                <Option v-for="item in tags" :value="item.id" :key="item.id">{{ item.name }}</Option>
              </Select>
            </FormItem>
            <FormItem label="私密文章" prop="protected">
              <i-switch v-model="form.protected" size="large">
                <span slot="open">私密</span>
                <span slot="close">公开</span>
              </i-switch>
            </FormItem>
            <Divider dashed/>
            <FormItem>
              <Button class="publish-button">预览</Button>
              <Button class="publish-button">保存草稿</Button>
              <Button class="publish-button"
                      type="primary"
                      style="width:90px;"
                      icon="ios-checkmark-circle"
                      :loading="publishing"
                      @click="handlePublish">
                  发表
              </Button>
            </FormItem>
          </Col>
        </Row>
      </Form>
    </Card>
  </div>
</template>

<script>
import MarkdownEditor from '_c/markdown'
import { listSources } from '@/api/source'
import { listCategories } from '@/api/category'
import { listTags } from '@/api/tag'
import { createArticle } from '@/api/article'

export default {
  name: 'admin_article_post',
  components: {
    MarkdownEditor
  },
  data () {
    return {
      sources: [],
      categories: [],
      tags: [],
      tagLoading: false,
      tagNotFoundText: '无匹配数据',
      fakeTagPrefix: 'newtag-',
      publishing: false,
      form: {
        title: '',
        summary: '',
        content: '',
        sourceId: '',
        categoryId: [],
        tags: [],
        protected: false
      },
      rules: {
        title: [
          { required: true, message: '文章标题不能为空', trigger: 'blur' },
          { type: 'string', max: 255, message: '文章标题最多255个字符' }
        ],
        summary: [
          { type: 'string', max: 255, message: '文章摘要最多255个字符' }
        ],
        content: [
          { required: true, message: '文章内容不能为空', trigger: 'blur' }
        ],
        sourceId: [
          { required: true, message: '文章来源不能为空', trigger: 'blur' }
        ],
        categoryId: [
          { type: 'array', required: true, message: '文章分类不能为空', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    getSources () {
      return new Promise((resolve, reject) => {
        listSources().then(res => {
          this.sources = res.sources
          resolve()
        }).catch(err => {
          const response = err.response
          const data = response.data
          this.$Message.error(data.error.message)
        })
      })
    },
    getCategories () {
      let params = {
        parent_id: ''
      }
      return new Promise((resolve, reject) => {
        listCategories(params).then(res => {
          for (var item of res.categories) this.categories.push({value: item.id, label: item.name, children: [], loading: false})
          resolve()
        }).catch(err => {
          const response = err.response
          const data = response.data
          this.$Message.error(data.error.message)
        })
      })
    },
    loadSubCategories (item, callback) {
      item.loading = true
      let params = {
        parent_id: item.value
      }
      return new Promise((resolve, reject) => {
        listCategories(params).then(res => {
          item.loading = false
          for (var it of res.categories) item.children.push({value: it.id, label: it.name})
          callback()
          resolve()
        }).catch(err => {
          item.loading = false
          const response = err.response
          const data = response.data
          this.$Message.error(data.error.message)
        })
      })
    },
    categoryFormat (labels, selectedData) {
      if (labels.length) return labels[0] + ' - ' + labels[1]
      else return ''
    },
    tagRemoteSearch (query) {
      query = query.trim()
      if (query !== '' && this.form.tags.length < 5) {
        this.tagLoading = true
        let params = {
          name: query
        }
        return new Promise((resolve, reject) => {
          listTags(params).then(res => {
            this.tagLoading = false
            let tags = []
            let allMatch = false
            for (var item of res.tags) {
              if (item.name === query) allMatch = true
              tags.push({id: item.id, name: item.name})
            }
            // NOTE: if perfectly  match tag not exist, create a fake tag here
            if (!allMatch) tags.push({id: this.fakeTagPrefix + query, name: query})
            this.tags = tags
            resolve()
          }).catch(err => {
            this.tagLoading = false
            const response = err.response
            const data = response.data
            this.$Message.error(data.error.message)
          })
        })
      } else this.tags = []
    },
    onTagSelectChange (params) {
      this.tagNotFoundText = (params.length >= 5 ? '所选标签已达到5个' : '无匹配数据')
    },
    handlePublish () {
      this.$refs.postForm.validate((valid) => {
        if (valid) {
          let params = {
            title: this.form.title,
            content: this.form.content,
            sourceId: this.form.sourceId,
            categoryId: this.form.categoryId.slice(-1)[0],
            published: true,
            summary: this.form.summary,
            protected: this.form.protected
          }
          let tags = []
          for (var tag of this.form.tags) {
            if (tag.startsWith(this.fakeTagPrefix)) tags.push({id: null, name: tag.substr(this.fakeTagPrefix.length)})
            else tags.push({id: tag, name: null})
          }
          if (tags.length) params['tags'] = tags
          this.publishing = true
          return new Promise((resolve, reject) => {
            createArticle(params).then(res => {
              this.publishing = false
              this.$Message.info('文章发表成功')
              resolve()
            }).catch(err => {
              this.publishing = false
              const response = err.response
              const data = response.data
              this.$Message.error(data.error.message)
            })
          })
        }
      })
    }
  },
  mounted () {
    this.getSources()
    this.getCategories()
  }
}
</script>

<style lang="less">
.publish-button{
    float: right;
    margin-left: 10px;
}
</style>
