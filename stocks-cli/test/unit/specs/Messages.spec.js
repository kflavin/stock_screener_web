import Vue from 'vue'
import Messages from '@/components/home/Messages'

function getRenderedText (Component, propsData) {
  const Ctor = Vue.extend(Component);
  const vm = new Ctor().$mount();
  return vm.$el.textContent;
}

describe('Messages.vue', () => {
  it('renders content correctly', () => {
    console.log(getRenderedText(Messages))
    expect(getRenderedText(Messages)).to.equal("Messages")
  });
});
