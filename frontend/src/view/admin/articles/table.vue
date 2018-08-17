<template>
  <div>
    <Card>
      <tables ref="table"
              border
              editable
              searchable
              search-place="top"
              :loading="loading"
              v-model="tableData"
              :columns="columns"
              @on-sort-change="handleSortChange"
              @on-save-edit="handleEdit"
              :custom-search="true"
              @on-search="handleSearch"
              @on-delete="handleDelete">
      <span slot="toolbox" style="margin-left: 2px;">
        <Select v-model="showWhat" style="width: 150px;">
          <Option value="all" key="all">显示所有</Option>
          <Option value="published" key="published">只显示已发表</Option>
          <Option value="draft" key="draft">只显示草稿</Option>
        </Select>
        <Select v-model="showSelfOrAll" style="width: 150px; margin-left: 2px;">
          <Option value="all" key="all">看所有人</Option>
          <Option value="self" key="published">只看自己</Option>
        </Select>
        <AddArticle/>
      </span>
      </tables>
      <div style="margin: 10px;overflow: hidden">
        <div style="float: right;">
            <Page show-sizer
                  :total="dataTotal"
                  :page-size-opts="pageSizeOpts"
                  :page-size="pageSize"
                  :current="currentPage"
                  @on-change="changePage"
                  @on-page-size-change="changePageSize"/>
        </div>
      </div>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import AddArticle from './add.vue'
import { listArticles, deleteArticle } from '@/api/article'
import { EventBus } from '@/libs/bus'

export default {
  name: 'ArticleTable',
  components: {
    Tables,
    AddArticle
  },
  data () {
    return {
      // 初始化数据总条数
      dataTotal: 0,
      // 分页显示条数默认为10
      pageSize: 10,
      pageSizeOpts: [10, 25, 50, 100],
      // 当前所在分页索引
      currentPage: 1,
      // sort related
      sortColumn: 'published_at',
      SortDirection: 'desc',
      // filter related
      searchKey: '',
      searchValue: '',
      tableData: [],
      //
      showWhat: 'published',
      showSelfOrAll: 'self',
      columns: [
        {
          title: 'Title',
          key: 'title',
          width: 250,
          editable: false,
          sortable: true,
          searchable: true,
          render: (h, params) => {
            let slot = (params.row.published ? '' : '[草稿]') + params.row.title
            return h('span', slot)
          }
        },
        {
          title: 'Source',
          key: 'source',
          width: 100,
          sortable: true,
          render: (h, params) => {
            const colors = {
              '原创': 'primary',
              '转载': 'success',
              '翻译': 'warning'
            }
            let source = params.row.source.name
            let color = colors[source] || 'error'
            return h('Tag', {
              props: {
                color: color,
                fade: true
              }
            }, source)
          }
        },
        {
          title: 'Category',
          key: 'category',
          width: 200,
          render: (h, params) => {
            let category = []
            for (var item of params.row.category) category.push(item.name)
            return h('Tag', category.join(' - '))
          }
        },
        {
          title: 'Tags',
          key: 'tags',
          width: 250,
          render: (h, params) => {
            let tags = []
            for (var tag of params.row.tags) tags.push(h('Tag', tag.name))
            return h('Row', tags)
          }
        },
        {
          title: 'Author',
          key: 'user',
          width: 100,
          searchable: true,
          ellipsis: true,
          tooltip: true,
          render: (h, params) => {
            return h('p', params.row.user.name)
          }
        },
        // {title: 'Create-Time', key: 'created_at', sortable: true},
        {title: 'Views', key: 'views', width: 100},
        {title: 'Stars', key: 'stars', width: 100},
        {
          title: 'Publish-Time',
          key: 'published_at',
          width: 150,
          sortable: true,
          sortType: 'desc',
          render: (h, params) => {
            if (params.row.published_at) {
              return h('Time', {
                props: {
                  time: params.row.published_at,
                  interval: 60
                }
              })
            } else return h('span', '-')
          }
        },
        {
          title: 'Create-Time',
          key: 'created_at',
          width: 150,
          sortable: true,
          render: (h, params) => {
            return h('Time', {
              props: {
                time: params.row.created_at,
                interval: 60
              }
            })
          }
        },
        {
          title: 'Handle',
          key: 'handle',
          button: [
            (h, params, vm) => {
              return h('Button', {
                props: {
                  // type: 'dashed',
                  icon: 'logo-markdown'
                },
                style: {
                  marginRight: '2px'
                },
                on: {
                  click: () => {
                    let args = { article_id: params.row.id }
                    this.$router.push({
                      name: 'admin_article_edit',
                      params: args
                    })
                  }
                }
              }, '编辑')
            },
            (h, params, vm) => {
              let title = params.row.title
              return h('Poptip', {
                props: {
                  confirm: true,
                  title: `你确定要删除文章"${title}"吗?`
                },
                on: {
                  'on-ok': () => {
                    vm.$emit('on-delete', params)
                  }
                }
              }, [
                h('Button', {
                  props: {
                    // type: 'dashed',
                    icon: 'md-trash'
                  }
                }, '删除')
              ])
            }
          ]
        }
      ],
      loading: false
    }
  },
  methods: {
    getTableData () {
      this.loading = true
      let params = {
        page: this.currentPage,
        pageSize: this.pageSize,
        sort: this.sortColumn,
        direction: this.SortDirection
      }
      if (this.showWhat === 'published') params['published'] = true
      else if (this.showWhat === 'draft') params['published'] = false
      if (this.showSelfOrAll === 'self') params['user_id'] = this.$store.state.user.id
      if (this.searchKey) params[this.searchKey] = this.searchValue.trim()
      return new Promise((resolve, reject) => {
        listArticles(params).then(res => {
          this.tableData = res.articles
          this.dataTotal = res.total
          this.loading = false
          resolve()
        }).catch(err => {
          this.loading = false
          const response = err.response
          const data = response.data
          this.$Message.error(data.error.message)
        })
      })
    },
    changePage (index) {
      this.currentPage = index
      this.getTableData()
    },
    changePageSize (size) {
      this.pageSize = size
      this.getTableData()
    },
    handleSortChange ({column, key, order}) {
      this.sortColumn = key
      this.SortDirection = order
      this.getTableData()
    },
    handleSearch ({key, value}) {
      this.searchKey = key
      this.searchValue = value
      this.getTableData()
    },
    handleEdit (params) {
      console.log(params)
    },
    handleDelete (params) {
      let id = params.row.id
      let title = params.row.title
      this.loading = true
      return new Promise((resolve, reject) => {
        deleteArticle(id).then(res => {
          this.loading = false
          this.$Message.info(`文章${title}删除成功`)
          this.getTableData()
          resolve()
        }).catch(err => {
          this.loading = false
          const response = err.response
          const data = response.data
          if ([404].includes(response.status)) {
            this.$Message.info(`文章${title}删除成功`)
            this.getTableData()
          } else {
            this.$Message.error(data.error.message)
          }
        })
      })
    }
  },
  mounted () {
    EventBus.$on('articleCreated', () => {
      this.getTableData()
    })
    this.getTableData()
  },
  watch: {
    showWhat (val) {
      this.getTableData()
    }
  }
}
</script>
