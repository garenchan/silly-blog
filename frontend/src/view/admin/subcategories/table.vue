<template>
  <div>
    <Card>
      <p slot="title">
        <Icon type="ios-help-buoy"></Icon>
        所属分类: {{ name }}
      </p>
      <tables ref="table"
              editable searchable
              search-place="top"
              :loading="loading"
              v-model="tableData"
              :columns="columns"
              @on-sort-change="handleSortChange"
              @on-save-edit="handleEdit"
              :custom-search="true"
              @on-search="handleSearch"
              @on-delete="handleDelete"
              @on-order-change="handleOrderChange"
              @on-protected-change="handleProtectedChange">
        <AddCategory slot="toolbox" :parentId="id" :parentName="name"/>
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
import AddCategory from './add.vue'
import { listCategory, getCategory, updateCategory, deleteCategory } from '@/api/category'
import { EventBus } from '@/libs/bus'

export default {
  name: 'SubCategoryTable',
  components: {
    Tables,
    AddCategory
  },
  data () {
    return {
      // 当前一级分类的信息
      id: this.$route.params.category_id,
      name: '',
      // 初始化数据总条数
      dataTotal: 0,
      // 分页显示条数默认为10
      pageSize: 10,
      // 当前所在分页索引
      currentPage: 1,
      // sort related
      sortColumn: 'display_order',
      SortDirection: 'asc',
      // filter related
      searchKey: '',
      searchValue: '',
      tableData: [],
      columns: [
        // {type: 'selection', key: 'id', width: 60, align: 'center'},
        {title: 'Name', key: 'name', editable: true, sortable: true, searchable: true},
        {title: 'Description', key: 'description', editable: true, sortable: true, searchable: true},
        {
          title: 'Order',
          key: 'display_order',
          sortable: true,
          sortType: 'asc',
          render: (h, params) => {
            return h('InputNumber', {
              props: {
                value: params.row.display_order,
                editable: false
              },
              on: {
                'on-change': (value) => {
                  this.$refs.table.$emit('on-order-change', Object.assign(params, {value: value}))
                }
              }
            })
          }
        },
        {
          title: 'Protected',
          key: 'protected',
          sortable: false,
          render: (h, params) => {
            return h('i-switch', {
              props: {
                // type: 'primary',
                size: 'large',
                value: params.row.protected,
                loading: false
              },
              on: {
                'on-change': (value) => {
                  this.$refs.table.$emit('on-protected-change', Object.assign(params, {value: value}))
                }
              }
            }, [
              h('span', {
                slot: 'open'
              }, '隐藏'),
              h('span', {
                slot: 'close'
              }, '公开')
            ])
          }
        },
        {title: 'Create-Time', key: 'created_at', sortable: true},
        {title: 'Update-Time', key: 'updated_at', sortable: true},
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
                  title: `你确定要删除二级分类"${name}"吗?`
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
                }, '删除二级分类')
              ])
            }
          ]
        }
      ],
      loading: false
    }
  },
  methods: {
    getCategoryInfo () {
      return new Promise((resolve, reject) => {
        getCategory(this.id).then(res => {
          this.name = res.category.name
        }).catch(err => {
          console.log(err)
        })
      })
    },
    getTableData () {
      this.loading = true
      let params = {
        page: this.currentPage,
        pageSize: this.pageSize,
        sort: this.sortColumn,
        direction: this.SortDirection,
        parent_id: this.id
      }
      if (this.searchKey) params[this.searchKey] = this.searchValue
      return new Promise((resolve, reject) => {
        listCategory(params).then(res => {
          this.tableData = res.categories
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
        deleteCategory(id).then(res => {
          this.loading = false
          this.$Message.info(`二级分类${name}删除成功`)
          this.getTableData()
          resolve()
        }).catch(err => {
          this.loading = false
          const response = err.response
          const data = response.data
          if ([404].includes(response.status)) {
            this.$Message.info(`二级分类${name}删除成功`)
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
      let keyMap = {
        name: '分类名',
        description: '分类描述'
      }
      this.loading = true
      return new Promise((resolve, reject) => {
        updateCategory(id, data).then(res => {
          this.loading = false
          this.$Message.info('二级分类编辑成功')
          this.$set(this.tableData[params.index], key, res.category[key])
          this.$set(this.tableData[params.index], 'updated_at', res.category.updated_at)
          resolve()
        }).catch(err => {
          this.loading = false
          const response = err.response
          const data = response.data
          if (response.status === 409) {
            this.$Message.error(`${keyMap[key]}${curValue}已存在`)
          } else {
            this.$Message.error(data.error.message)
          }
          this.$set(this.tableData[params.index], key, origValue)
        })
      })
    },
    handleOrderChange (params) {
      let id = params.row.id
      let origValue = params.row.display_order
      let curValue = params.value
      if (origValue === curValue) return
      let name = params.row.name
      this.loading = true
      return new Promise((resolve, reject) => {
        updateCategory(id, {display_order: curValue}).then(res => {
          this.loading = false
          this.$Message.info(`二级分类"${name}"调整显示顺序成功`)
          this.getTableData()
          resolve()
        }).catch(err => {
          this.loading = false
          const response = err.response
          const data = response.data
          this.$Message.error(data.error.message)
          this.getTableData()
          reject(err)
        })
      })
    },
    handleProtectedChange (params) {
      let id = params.row.id
      let origValue = params.row.enabled
      let curValue = params.value
      if (origValue === curValue) return
      let name = params.row.name
      let action = curValue ? '隐藏' : '公开'
      this.loading = true
      return new Promise((resolve, reject) => {
        updateCategory(id, {protected: curValue}).then(res => {
          this.loading = false
          this.$Message.info(`二级分类"${name}"${action}成功`)
          this.$set(this.tableData[params.index], 'protected', res.category.protected)
          resolve()
        }).catch(err => {
          this.loading = false
          const response = err.response
          const data = response.data
          this.$Message.error(data.error.message)
          // TODO: while request failed, restore switch
          this.$set(this.tableData[params.index], 'protected', origValue)
          reject(err)
        })
      })
    }
  },
  mounted () {
    EventBus.$on('categoryCreated', () => {
      this.getTableData()
    })
    this.getCategoryInfo()
    this.getTableData()
  }
}
</script>
