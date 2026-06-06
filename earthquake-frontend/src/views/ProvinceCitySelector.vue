<template>
  <div class="province-city-selector">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-select
          v-model="selectedProvinceId"
          placeholder="选择省份"
          clearable
          @change="handleProvinceChange"
          style="width: 100%"
        >
          <el-option
            v-for="province in provinces"
            :key="province.province_id"
            :label="province.province_name"
            :value="province.province_id"
          />
        </el-select>
      </el-col>
      <el-col :span="12">
        <el-select
          v-model="selectedCityId"
          placeholder="选择城市"
          clearable
          @change="handleCityChange"
          style="width: 100%"
        >
          <el-option
            v-for="city in cities"
            :key="city.city_id"
            :label="city.city_name"
            :value="city.city_id"
          />
        </el-select>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { getProvinces, getCities } from '../API/common'

export default {
  name: 'ProvinceCitySelector',
  props: {
    // 是否显示全部选项
    showAll: {
      type: Boolean,
      default: false
    }
  },
  emits: ['change'],
  data() {
    return {
      provinces: [],
      cities: [],
      selectedProvinceId: null,
      selectedCityId: null
    }
  },
  mounted() {
    this.loadProvinces()
  },
  methods: {
    async loadProvinces() {
      try {
        const response = await getProvinces()
        if (response.code === 200) {
          this.provinces = response.data
        }
      } catch (error) {
        console.error('加载省份列表失败:', error)
      }
    },
    async handleProvinceChange(provinceId) {
      this.selectedCityId = null
      this.cities = []

      if (!provinceId) {
        this.emitChange()
        return
      }

      try {
        const response = await getCities({ province_id: provinceId })
        if (response.code === 200) {
          this.cities = response.data
        }
      } catch (error) {
        console.error('加载城市列表失败:', error)
      }

      this.emitChange()
    },
    handleCityChange() {
      this.emitChange()
    },
    emitChange() {
      this.$emit('change', {
        province_id: this.selectedProvinceId,
        city_id: this.selectedCityId
      })
    }
  }
}
</script>

<style scoped>
.province-city-selector {
  margin-bottom: 20px;
}
</style>
