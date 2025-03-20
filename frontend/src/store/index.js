import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    videoInfo: null, // 存储爬取的视频信息
    bvid: "", // 存储当前的 BV 号
  },
  mutations: {
    setVideoInfo(state, videoInfo) {
      state.videoInfo = videoInfo;
    },
    setBvid(state, bvid) {
      state.bvid = bvid;
    },
  },
  actions: {
    updateVideoInfo({ commit }, videoInfo) {
      commit("setVideoInfo", videoInfo);
    },
    updateBvid({ commit }, bvid) {
      commit("setBvid", bvid);
    },
  },
});