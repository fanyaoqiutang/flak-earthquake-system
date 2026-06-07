import request from './request'

// 获取地震列表
export function getEarthquakeList(params) {
    return request({
        url: '/earthquake/list',
        method: 'get',
        params
    })
}

// 获取所有省份
export function getProvinces() {
    return request({
        url: '/provinces',
        method: 'get'
    })
}

// 获取所有城市（新增）
export function getCities(params) {
    return request({
        url: '/cities',
        method: 'get',
        params
    })
}

// 获取省份分组（按地区）
export function getProvincesGroup() {
    return request({
        url: '/province/group',
        method: 'get'
    })
}

// 获取省份地震统计（饼图）
export function getEarthquakeStatsProvince() {
    return request({
        url: '/earthquake/stats/province',
        method: 'get'
    })
}

// 获取城市地震统计（新增）
export function getEarthquakeStatsCity() {
    return request({
        url: '/earthquake/stats/city',
        method: 'get'
    })
}

// 获取时间趋势统计（折线图）
export function getEarthquakeStatsTrend() {
    return request({
        url: '/earthquake/stats/trend',
        method: 'get'
    })
}

// 获取震级分布统计（柱状图）
export function getEarthquakeStatsMagnitude() {
    return request({
        url: '/earthquake/stats/magnitude',
        method: 'get'
    })
}

// 获取地震频次 TOP5 排名（省份）
export function getEarthquakeRank() {
    return request({
        url: '/earthquake/rank',
        method: 'get'
    })
}

// 获取城市地震频次 TOP5 排名（新增）
export function getEarthquakeCityRank() {
    return request({
        url: '/earthquake/city_rank',
        method: 'get'
    })
}

// 获取综合统计数据
export function getEarthquakeStatistics(params) {
    return request({
        url: '/statistics',
        method: 'get',
        params
    })
}
