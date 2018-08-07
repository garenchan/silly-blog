<template>
  <div>
    <Card>
      <tables ref="table"
              editable searchable
              search-place="top"
              :loading="loading"
              :toolbox="toolbox"
              v-model="tableData"
              :columns="columns"
              @on-sort-change="handleSortChange"
              @on-save-edit="handleEdit"
              :custom-search="true"
              @on-search="handleSearch"
              @on-delete="handleDelete">
        <AddTag slot="toolbox"/>
      </tables>
      <div style="margin: 10px;overflow: hidden">
        <div style="float: right;">
            <Page :total="dataTotal" :page-size="pageSize" :current="currentPage" @on-change="changePage"></Page>
        </div>
      </div>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import AddTag from './add.vue'
import { listTags, updateTag, deleteTag } from '@/api/tag'
import { EventBus } from '@/libs/bus'

export default {
  name: 'TagTable',
  components: {
    Tables,
    AddTag
  },
  data () {
    return {
      // 初始化数据总条数
      dataTotal: 0,
      // 分页显示条数默认为10
      pageSize: 10,
      // 当前所在分页索引
      currentPage: 1,
      // sort related
      sortColumn: 'updated_at',
      SortDirection: 'desc',
      // filter related
      searchKey: '',
      searchValue: '',
      tableData: [],
      columns: [
        // {type: 'selection', key: 'id', width: 60, align: 'center'},
        {title: 'Name', key: 'name', editable: true, sortable: true, searchable: true},
        {title: 'Create-Time', key: 'created_at', sortable: true},
        {title: 'Update-Time', key: 'updated_at', sortable: true, sortType: 'desc'},
        {
          title: 'Handle',
          key: 'handle',
          // options: ['delete'],
          button: [
            (h, params, vm) => {
              let name = params.row.name
              return h('Poptip', {
                props: {
                  confirm: true,
                  title: `你确定要删除标签"${name}"吗?`
                },
                on: {
                  'on-ok': () => {
                    vm.$emit('on-delete', params)
                  }
                }
              }, [
                h('Button', {
                  props: {
                    type: 'dashed',
                    icon: 'md-trash'
                  }
                }, '删除标签')
              ])
            }
          ]
        }
      ],
      loading: false,
      toolbox: {
        'add': AddTag
      }
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
      if (this.searchKey) params[this.searchKey] = this.searchValue
      return new Promise((resolve, reject) => {
        listTags(params).then(res => {
          this.tableData = res.tags
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
    handleDelete (params) {
      let id = params.row.id
      let name = params.row.name
      this.loading = true
      return new Promise((resolve, reject) => {
        deleteTag(id).then(res => {
          this.loading = false
          this.$Message.info(`标签${name}删除成功`)
          this.getTableData()
          resolve()
        }).catch(err => {
          this.loading = false
          const response = err.response
          const data = response.data
          if ([404].includes(response.status)) {
            this.$Message.info(`标签${name}删除成功`)
            this.getTableData()
          } else {
            this.$Message.error(data.error.message)
          }
        })
      })
    },
    exportExcel () {
      this.$refs.table.exportCsv({
        filename: `table-${(new Date()).valueOf()}.csv`
      })
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
      let id = params.row.id
      let key = params.column.key
      let origValue = params.row[key]
      let curValue = params.value
      let data = {
        [key]: curValue
      }
      this.loading = true
      return new Promise((resolve, reject) => {
        updateTag(id, data).then(res => {
          this.loading = false
          this.$Message.info('标签名编辑成功')
          this.$set(this.tableData[params.index], key, res.tag[key])
          this.$set(this.tableData[params.index], 'updated_at', res.tag.updated_at)
          resolve()
        }).catch(err => {
          this.loading = false
          const response = err.response
          const data = response.data
          if (response.status === 409) {
            this.$Message.error(`标签名${curValue}已存在`)
          } else {
            this.$Message.error(data.error.message)
          }
          this.$set(this.tableData[params.index], key, origValue)
        })
      })
    }
  },
  mounted () {
    EventBus.$on('tagCreated', () => {
      this.getTableData()
    })
    this.getTableData()
  }
}
</script>
