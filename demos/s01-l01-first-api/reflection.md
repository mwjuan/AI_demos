# 第 1 课复盘

完成代码和实验后再填写。答案应来自你的观察，而不是复制定义。

## 能运行

- 三个提示词是否都成功？如果没有，失败发生在哪一层？
都成功了
- 三次请求的输入、输出和总 token 分别是多少？
direct：{ inputTokens: 14, outputTokens: 1143, totalTokens: 1157 }
audience：{ inputTokens: 37, outputTokens: 344, totalTokens: 381 }
example：{ inputTokens: 54, outputTokens: 373, totalTokens: 427 }
- 哪次响应最慢？单次实验能否证明提示词导致了这个差异？为什么？
direct响应最慢，实验证明是提示词导致了这个差异，我猜是因为其他两者的提示词中有角色的概念，所以框定了回答范围
<!-- 
direct：解释 JavaScript 闭包。
audience：向一位熟悉 React 和 Node.js、但刚开始学习 AI 的前端开发者解释 JavaScript 闭包。使用清晰、简短的中文。
example：向一位熟悉 React 和 Node.js、但刚开始学习 AI 的前端开发者解释 JavaScript 闭包。使用清晰、简短的中文，并给出一个能直接运行的最小例子，说明闭包保留了什么状态。
 -->

## 能解释

1. `direct`、`audience`、`example` 的回答分别发生了什么变化？
direct的回答有概念、示例、关键点、本质、用途、注意事项、测试、总结
audience的回答有概念、示例、关键点、类比
example的回答有概念、示例、关键点、类比
2. 为什么更详细的提示词通常更可控，却仍然不能保证事实正确？
详细的提示词加强了任务约束，但是模型根据训练预测接下来最可能的token，但不会子弟哦那个查询可靠的事实来源
3. 模型为什么可能给出语气自信但内容错误的答案？
因为模型的目标是生成连贯的、符合上下文的文字，当资料不足、问题模糊或者训练数据有误时就会产生幻觉
4. 为什么 API 密钥可以出现在 Node.js 服务端环境变量中，却不能放进 React 前端？
React前端中可以通过开发者工具看到密钥，造成密钥泄漏产生额外的额度消耗，服务端环境变量时不会发送给浏览器的，用户看不到所以是相对安全的
5. `inputTokens` 和 `outputTokens` 分别受什么影响？
inputTokens感觉是受输入内容长度，outputTokens是受回答内容长度

## 能修改

只改一个变量，设计第四个提示词。先写下你的预测，再运行至少三次，并记录结果是否支持预测。

- 修改的变量：用不超过 100 个汉字
- 预测：outputtoken会变小
- 观察：
第一次direct：{ inputTokens: 14, outputTokens: 1086, totalTokens: 1100 }
第一次direct：{ inputTokens: 14, outputTokens: 1279, totalTokens: 1293 }
第一次concise：{ inputTokens: 23, outputTokens: 45, totalTokens: 68 }
- 结论：加强任务约可以减少outputToken

## 卡点记录

- 我看到的现象：
- 我原本预期：
- 我的猜测：
- 我已经尝试：
- 我现在的问题：

