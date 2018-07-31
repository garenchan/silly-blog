<template>
  <div>
    <Card>
      <tables ref="tables" editable searchable search-place="top" v-model="tableData" :columns="columns" @on-delete="handleDelete"/>
      <Button style="margin: 10px 0;" type="primary" @click="exportExcel">导出为Csv文件</Button>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import { getTagsInfo } from '@/api/tag'
export default {
  name: 'tag-table',
  components: {
    Tables
  },
  data () {
    return {
      columns: [
        {title: 'Name', key: 'name', editable: true, sortable: true},
        {title: 'Create-Time', key: 'created_at', sortable: true},
        {
          title: 'Handle',
          key: 'handle',
          options: [],
          button: [
          ]
        }
      ],
      tableData: []
    }
  },
  methods: {
    handleDelete (params) {
      console.log(params)
    },
    exportExcel () {
      this.$refs.tables.exportCsv({
        filename: `table-${(new Date()).valueOf()}.csv`
      })
    }
  },
  mounted () {
    getTagsInfo().then(res => {
      this.tableData = res.tags
    })
  }
}
</script>

<style>

</style>
