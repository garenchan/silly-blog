<template>
    <Slider v-model="value" range></Slider>
</template>
<script>
export default {
    name: 'MyFirst',
    data () {
        return {
            value: [20, 50]
        };
    }
};
</script>
