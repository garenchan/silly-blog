<template>
  <div>
    <Card>
      <Form ref="postForm" :model="form" :rules="rules" :label-width="80">
        <Row>
          <Col span="18">
            <FormItem label="文章标题" prop="title">
              <Input v-model="form.title" placeholder="请输入文章标题"/>
            </FormItem>
            <FormItem label="文章摘要" prop="summary">
              <Input v-model="form.summary" type="textarea" placeholder="请输入文章摘要"/>
            </FormItem>
            <FormItem label="文章内容" prop="content">
              <markdown-editor v-model="form.content"
                               preview-class="markdown-body"
                               :localCache="false"
                               :options="editorOptions"/>
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
              <i-switch v-model="form.protected"
                        size="large">
                <span slot="open">私密</span>
                <span slot="close">公开</span>
              </i-switch>
              &nbsp;<span style="color: #b3b3b3;">{{ protectedCaption }}</span>
            </FormItem>
            <Divider dashed/>
            <FormItem>
              <Button class="publish-button"
                      @click="handleClear">
                清空
              </Button>
              <Button v-if="!(isEdit && published)"
                      class="publish-button"
                      :loading="saving"
                      @click="handleSaveDraft">
                保存草稿
              </Button>
              <Button class="publish-button"
                      type="primary"
                      style="width:90px;"
                      icon="ios-checkmark-circle"
                      :loading="publishing"
                      @click="handlePublish">
                 {{ isEdit && published ? '保存': '发表'}}
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
import { createArticle, updateArticle, getArticle } from '@/api/article'
import hljs from 'highlight.js'

window.hljs = hljs
export default {
  name: 'admin_article_edit',
  components: {
    MarkdownEditor
  },
  data () {
    return {
      articleId: this.$route.params.article_id || '',
      published: false,
      sources: [],
      categories: [],
      tags: [],
      tagLoading: false,
      tagNotFoundText: '无匹配数据',
      fakeTagPrefix: 'newtag-',
      publishing: false,
      saving: false,
      // Markdown编辑器配置项
      editorOptions: {
        autoDownloadFontAwesome: false,
        placeholder: '使用Markdown开始编写你的文章...',
        renderingConfig: {
          codeSyntaxHighlighting: true
        },
        spellChecker: false,
        toolbar: [
          'bold',
          'italic',
          'strikethrough',
          '|',
          'heading',
          'heading-smaller',
          'heading-bigger',
          'heading-1',
          'heading-2',
          'heading-3',
          '|',
          'code',
          'quote',
          'unordered-list',
          'ordered-list',
          'clean-block',
          '|',
          'link',
          'image',
          'table',
          'horizontal-rule',
          '|',
          'preview',
          'side-by-side',
          'fullscreen',
          '|',
          'guide'
        ],
        indentWithTabs: false,
        tabSize: 4
      },
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
          { required: true, message: '文章标题不能为空', trigger: 'change' },
          { type: 'string', max: 255, message: '文章标题最多255个字符' }
        ],
        summary: [
          { required: true, message: '文章摘要不能为空', trigger: 'change' },
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
  computed: {
    isEdit () {
      return Boolean(this.$route.params.article_id)
    },
    protectedCaption: function () {
      return this.form.protected ? '仅自己可见' : '所有人可见'
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
          for (var item of res.categories) {
            let subs = []
            for (var sub of item.subs) subs.push({ value: sub.id, label: sub.name })
            if (subs.length) this.categories.push({ value: item.id, label: item.name, children: subs })
          }
          resolve()
        }).catch(err => {
          const response = err.response
          const data = response.data
          this.$Message.error(data.error.message)
        })
      })
    },
    /*
     * If current operation is editing, get the article detail !
     */
    getCurrentArticle () {
      if (this.isEdit && this.articleId) {
        return new Promise((resolve, reject) => {
          getArticle(this.articleId).then(res => {
            this.form.title = res.article.title
            this.form.summary = res.article.summary
            this.form.content = res.article.content
            this.form.sourceId = res.article.source.id
            for (var category of res.article.category) this.form.categoryId.push(category.id)
            for (var tag of res.article.tags) {
              this.tags.push({ id: tag.id, name: tag.name })
              this.form.tags.push(tag.id)
            }
            this.published = res.article.published
            resolve()
          }).catch(err => {
            const response = err.response
            const data = response.data
            this.$Message.error(data.error.message)
          })
        })
      }
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
              tags.push({ id: item.id, name: item.name })
            }
            // NOTE: if perfectly  match tag not exist, create a fake tag here
            if (!allMatch) tags.push({ id: this.fakeTagPrefix + query, name: query })
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
    clearForm () {
      this.articleId = ''
      Object.assign(this.form, {
        title: '',
        summary: '',
        content: '',
        sourceId: '',
        categoryId: [],
        tags: [],
        protected: false
      })
    },
    handleSubmit (isPublish) {
      this.$refs.postForm.validate((valid) => {
        if (valid) {
          let params = {
            title: this.form.title,
            content: this.form.content,
            sourceId: this.form.sourceId,
            categoryId: this.form.categoryId.slice(-1)[0],
            published: Boolean(isPublish),
            summary: this.form.summary,
            protected: this.form.protected
          }
          let tags = []
          for (var tag of this.form.tags) {
            if (tag.startsWith(this.fakeTagPrefix)) tags.push({ id: null, name: tag.substr(this.fakeTagPrefix.length) })
            else tags.push({id: tag, name: null})
          }
          if (tags.length) params['tags'] = tags
          if (isPublish) this.publishing = true
          else this.saving = true
          return new Promise((resolve, reject) => {
            let promise = null
            if (this.articleId) promise = updateArticle(this.articleId, params)
            else promise = createArticle(params)
            return promise.then(res => {
              let message = null
              if (isPublish) {
                this.publishing = false
                if (this.isEdit) message = '文章保存成功'
                else message = '文章发表成功'
              } else {
                this.saving = false
                message = '文章已保存为草稿'
              }
              this.$Message.info(message)
              if (!this.isEdit) {
                // 在发表页
                if (isPublish) this.clearForm()
                else this.articleId = res.article.id
              } else {
                // 在编辑页
                if (isPublish) this.published = true
              }
              resolve()
            }).catch(err => {
              if (isPublish) this.publishing = false
              else this.saving = false
              const response = err.response
              const data = response.data
              this.$Message.error(JSON.stringify(data.error.message))
            })
          })
        }
      })
    },
    handlePublish () {
      this.handleSubmit(true)
    },
    handleSaveDraft () {
      this.handleSubmit(false)
    },
    handleClear () {
      // NOTE: The form's resetFields method can't clear itself completely
      // this.$refs.postForm.resetFields()
      this.clearForm()
    }
  },
  mounted () {
    this.getSources()
    this.getCategories()
    if (this.isEdit) this.getCurrentArticle()
  }
}
</script>

<style lang="less">
@import '~font-awesome/css/font-awesome.css';
@import '~github-markdown-css/github-markdown.css';
@import '~highlight.js/styles/atom-one-dark.css';
.publish-button{
    float: right;
    margin-left: 10px;
}
.markdown-wrapper{
  .CodeMirror, .CodeMirror-scroll {
    min-height: 450px;
  }
}
</style>
