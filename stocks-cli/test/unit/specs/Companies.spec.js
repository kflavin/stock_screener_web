import Vue from 'vue'
import Companies from '@/components/home/Companies'

function getRenderedText (Component, propsData) {
  const Ctor = Vue.extend(Component);
  const vm = new Ctor().$mount();
  return vm.$el.textContent;
}

describe('Companies.vue', () => {
  it('renders content correctly', () => {
    console.log(getRenderedText(Companies))
    expect(getRenderedText(Companies)).to.equal("Companies")
  });
});
