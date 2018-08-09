<template>
  <div>
    <Card>
        <Form :label-width="80">
            <Row>
              <Col span="18">
                <FormItem label="文章标题">
                    <Input v-model="form.title"/>
                </FormItem>
                <FormItem label="文章内容">
                    <markdown-editor v-model="form.content"/>
                </FormItem>
              </Col>
              <Col span="6">
                222
              </Col>
            </Row>
        </Form>
    </Card>
  </div>

</template>

<script>
import MarkdownEditor from '_c/markdown'

export default {
  name: 'markdown_page',
  components: {
    MarkdownEditor
  },
  data () {
    return {
      form: {
        title: '',
        content: ''
      }
    }
  }
}
</script>
