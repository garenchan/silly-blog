<template>
  <div>
    <Card>
      <tables ref="tables" editable searchable search-place="top" test="handle" v-model="tableData" :columns="columns" @on-delete="handleDelete"/>
      <Button style="margin: 10px 0;" type="primary" @click="exportExcel">导出为Csv文件</Button>
      <tag-handle></tag-handle>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import TagHandle from './handle.vue'
import { getTagsInfo } from '@/api/tag'

export default {
  name: 'TagTable',
  components: {
    Tables,
    TagHandle
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
      tableData: [],
      handle: TagHandle
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
    this.handle = TagHandle
    getTagsInfo().then(res => {
      this.tableData = res.tags
    })
  }
}
</script>

<style>

</style>
