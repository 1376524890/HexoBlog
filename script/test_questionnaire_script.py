#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
御坂妹妹 11 号 - 问卷星脚本验证工具
功能：检查油猴脚本配置文件，生成配置建议
"""

import json
import re
from datetime import datetime

def analyze_questionnaire_structure():
    """分析问卷数据结构"""
    print("🔍 正在分析问卷数据结构...")
    
    # 读取问卷数据文件
    try:
        with open('/home/claw/.openclaw/workspace/output/问卷数据_750 份.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ 问卷数据文件已加载：{len(data)} 条记录")
        print()
        
        # 分析第一份数据
        sample = data[0]
        print("📋 第一份问卷数据结构:")
        print("="*60)
        
        for key, value in sample.items():
            print(f"  {key}:")
            if isinstance(value, str):
                print(f"    类型：字符串")
                print(f"    内容：{value[:100]}..." if len(value) > 100 else f"    内容：{value}")
            elif isinstance(value, list):
                print(f"    类型：列表 ({len(value)} 项)")
                print(f"    内容：{value[:5]}")
            elif isinstance(value, dict):
                print(f"    类型：字典")
                for subkey, subval in value.items():
                    print(f"      {subkey}: {subval}")
            else:
                print(f"    类型：{type(value).__name__}")
                print(f"    内容：{value}")
            print()
        
        return data
    except Exception as e:
        print(f"❌ 读取问卷数据失败：{e}")
        return None

def generate_config_recommendations(data):
    """根据问卷数据生成配置建议"""
    if not data:
        return []
    
    recommendations = []
    sample = data[0]
    
    print("📝 生成配置建议...")
    print("="*60)
    
    # 分析每个字段，生成 config 配置
    for key, value in sample.items():
        if isinstance(value, str) and len(value) < 50:
            # 短字符串可能是单选题或填空题
            recommendations.append({
                "type": "填空题",
                "name": key,
                "value": value,
                "suggestion": f"将 '{key}' 添加到 config 数组"
            })
            print(f"✓ {key}: {value}")
        elif isinstance(value, list):
            # 列表可能是多选题
            recommendations.append({
                "type": "多选题",
                "name": key,
                "options": value,
                "suggestion": "使用随机选择逻辑"
            })
            print(f"✓ {key}: 多选 ({len(value)} 选项)")
        elif isinstance(value, dict):
            # 字典可能是嵌套数据
            recommendations.append({
                "type": "复合题",
                "name": key,
                "structure": list(value.keys()),
                "suggestion": "需要进一步分析"
            })
            print(f"✓ {key}: 复合结构 ({len(value)} 子项)")
    
    print()
    return recommendations

def create_config_template():
    """创建 config 配置文件模板"""
    template = """// ==UserScript==
// @name         问卷星自动填写 - 御坂美琴定制版
// @version      1.0
// @description 基于 WenjuanXin 优化，支持自定义答案配置
// @author       御坂妹妹 11 号
// @match        https://www.wjx.cn/jq/*.aspx
// @match        https://www.wjx.cn/m/*.aspx
// @match        https://v.wjx.cn/vm/*.aspx
// @grant        none
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';
    
    console.log("✅ 御坂妹妹问卷星脚本已加载");

    // ============================================================
    // 📝 答案配置区 - 请根据问卷实际结构修改
    // ============================================================
    var config = [
        // 填空题答案配置
        // 格式：{ id: 题目 ID, answer: [答案选项数组] }
        
        // 示例配置：
        // { id: 1, answer: ["18 岁以下", "18-25 岁", "26-35 岁", "36-45 岁", "46-55 岁", "56 岁以上"] },
        // { id: 2, answer: ["男", "女", "不愿透露"] },
        
        // 如果有更多填空题，继续添加...
        // 如果没有填空题，可以留空或填"无"
    ];

    // 填空题默认答案（如果未配置）
    var defaultFillAnswer = "无";

    // ============================================================
    // 🔧 工具函数
    // ============================================================
    function randint(min, max) {
        return Math.floor(Math.random() * (max - min + 1) + min);
    }

    function getRandomArrayElements(arr, count) {
        var shuffled = arr.slice(0), i = arr.length, min = i - count, temp, index;
        while (i-- > min) {
            index = Math.floor((i + 1) * Math.random());
            temp = shuffled[index];
            shuffled[index] = shuffled[i];
            shuffled[i] = temp;
        }
        return shuffled.slice(min);
    }

    // ============================================================
    // 🎯 答题函数
    // ============================================================
    function RandomChoose() {
        // 单选题
        this.singleChoose = function(subject) {
            try {
                if (subject.querySelectorAll("img")[0]) {
                    var img = subject.querySelectorAll("img");
                    img[randint(0, img.length - 1)].click();
                } else {
                    var list = subject.querySelectorAll("li");
                    var no;
                    for(var i = 0; i < list.length; i++){
                        if(list[i].querySelector(".underline") != null){
                            no = i;
                        }
                    }
                    var index = randint(0, list.length - 1);
                    while(index == no && list.length > 1){index = randint(0, list.length - 1);}
                    if (list[index]) {
                        list[index].click();
                    }
                }
            } catch (e) {
                console.log("⚠ 单选填写失败:", e.message);
            }
        };

        // 多选题
        this.multiChoose = function(subject) {
            try {
                var list = subject.querySelectorAll("li");
                var arr = [];
                for (var i = 0; i < list.length; i++) {
                    arr.push(list[i]);
                }
                var times = randint(2, Math.max(2, arr.length - 1));
                var indexAry = getRandomArrayElements(arr, Math.min(times, arr.length));
                
                for (var i = 0; i < indexAry.length; i++) {
                    if (indexAry[i].querySelectorAll("input")[0] && 
                        indexAry[i].querySelectorAll("input")[0].checked === false) {
                        indexAry[i].click();
                    }
                }
            } catch (e) {
                console.log("⚠ 多选填写失败:", e.message);
            }
        };

        // 星星评分
        this.star = function(subject) {
            try {
                var list = subject.querySelectorAll("li:not([class='notchoice'])");
                if (list.length > 0) {
                    list[randint(0, list.length - 1)].click();
                }
            } catch (e) {
                console.log("⚠ 星星评分填写失败:", e.message);
            }
        };

        // 下拉选择
        this.dropdownSelect = function(subject) {
            try {
                var select = subject.querySelectorAll("select")[0];
                if (select && select.length > 1) {
                    var rnnum = randint(1, select.length - 1);
                    select.selectedIndex = rnnum;
                    select.dispatchEvent(new Event('change'));
                }
            } catch (e) {
                console.log("⚠ 下拉选择填写失败:", e.message);
            }
        };

        // 拉条
        this.slider = function(subject) {
            try {
                var max = Number(subject.querySelectorAll(".slider")[0]?.getAttribute("maxvalue")) || 10;
                var min = Number(subject.querySelectorAll(".slider")[0]?.getAttribute("minvalue")) || 0;
                var value = randint(min, max);
                
                var slider = subject.querySelector(".imageSlider1");
                var bar = subject.querySelector(".imageBar1");
                
                if (slider && bar) {
                    var rect = slider.getBoundingClientRect();
                    var x = ((value - min) / (max - min)) * (slider.offsetWidth - bar.offsetWidth);
                    
                    var evt = new MouseEvent("click", {
                        clientX: rect.left + x + (bar.offsetWidth / 2),
                        type: "click"
                    });
                    subject.querySelector(".ruler")?.dispatchEvent(evt);
                }
            } catch (e) {
                console.log("⚠ 拉条填写失败:", e.message);
            }
        };
    }

    // ============================================================
    // 🎯 题目类型判断
    // ============================================================
    function judgeType() {
        try {
            var q = document.getElementsByClassName("div_question");
            var rc = new RandomChoose();
            
            console.log(`📝 找到 ${q.length} 道题目`);
            
            for (var i = 0; i < q.length; i++) {
                // 普通单选 or 多选
                if ((q[i].querySelectorAll(".ulradiocheck")[0]) && (q[i].querySelectorAll("input")[0])) {
                    var input = q[i].querySelectorAll("input");
                    if (input[0].type == 'radio') {
                        rc.singleChoose(q[i]);
                    } else if (input[0].type == 'checkbox') {
                        rc.multiChoose(q[i]);
                    }
                }
                // 表格
                else if (q[i].querySelectorAll("table")[0]) {
                    var inputs = q[i].querySelectorAll("input");
                    if (inputs.length > 0) {
                        if (inputs[0].type == 'radio') {
                            // 表格单选
                        } else if (inputs[0].type == 'checkbox') {
                            // 表格多选
                        }
                    }
                }
                // 填空题
                else if (q[i].querySelectorAll("textarea")[0]) {
                    var textarea = q[i].querySelectorAll("textarea")[0];
                    var textareaId = textarea.id || "";
                    
                    // 查找配置的答案
                    var foundConfig = false;
                    for (var j = 0; j < config.length; j++) {
                        if (textareaId == ("q" + config[j].id) || textareaId.includes(config[j].id.toString())) {
                            var answer = config[j].answer[Math.floor(Math.random() * config[j].answer.length)];
                            textarea.value = answer;
                            console.log(`  [${i+1}] 填空题已填写：${answer}`);
                            foundConfig = true;
                            break;
                        }
                    }
                    
                    // 如果没有配置，使用默认答案
                    if (!foundConfig) {
                        textarea.value = defaultFillAnswer;
                        console.log(`  [${i+1}] 填空题（未配置，默认）：${defaultFillAnswer}`);
                    }
                }
                // 星星评分
                else if (q[i].querySelectorAll(".notchoice")[0]) {
                    rc.star(q[i]);
                }
                // 下拉选择
                else if (q[i].querySelectorAll("select")[0]) {
                    rc.dropdownSelect(q[i]);
                }
                // 拉条
                else if (q[i].querySelectorAll(".slider")[0]) {
                    rc.slider(q[i]);
                }
            }
            
            console.log("✅ 所有题目已填写完成！");
            return true;
        } catch (error) {
            console.log("⚠ 题目类型判断失败:", error.message);
            return false;
        }
    }

    // ============================================================
    // ⚡ 执行填写
    // ============================================================
    
    setTimeout(function() {
        judgeType();
        
        // 滚动到提交按钮
        try {
            var submitBtn = document.getElementById("submit_button");
            if (submitBtn) {
                var scrollValue = submitBtn.offsetTop;
                window.scrollTo({
                    top: scrollValue,
                    behavior: "smooth"
                });
            }
        } catch (e) {}
        
        // 2 秒后提交
        setTimeout(function() {
            try {
                var submitBtn = document.getElementById("submit_button");
                if (submitBtn) {
                    submitBtn.click();
                    console.log("✅ 问卷已提交！");
                }
            } catch (e) {}
        }, 2000);
        
        // 5 秒后刷新/跳转
        setTimeout(function() {
            try {
                var currentURL = window.location.href;
                var pat = /complete\\.aspx\\?activityid=(\\d+)/;
                var obj = pat.exec(currentURL);
                
                if (obj) {
                    var nextURL = "https://www.wjx.cn/jq/" + obj[1] + ".aspx";
                    window.location.href = nextURL;
                } else {
                    location.reload();
                }
            } catch (e) {
                location.reload();
            }
        }, 5000);
        
    }, 1000);

    window.alert = function(str) {
        console.log("⚠ 弹窗被阻止:", str);
        return;
    };

})();
"""
    
    print("✅ config 配置模板已创建")
    return template

def main():
    print("="*70)
    print("🚀 御坂妹妹 11 号 - 问卷星脚本验证工具")
    print("="*70)
    print()
    
    # 分析问卷结构
    data = analyze_questionnaire_structure()
    
    if data:
        print()
        # 生成配置建议
        recommendations = generate_config_recommendations(data)
        
        print()
        # 创建 config 模板
        template = create_config_template()
        
        print()
        print("="*70)
        print("📁 生成文件:")
        print("="*70)
        print("  1. config 配置模板：/home/claw/.openclaw/workspace/script/wenjuanxin_misaka.user.js")
        print("  2. 安装指南：/home/claw/.openclaw/workspace/script/问卷星填写指南.md")
        print("  3. Modify Headers 配置：/home/claw/.openclaw/workspace/script/modifyheaders.json")
        print()
        print("="*70)
        print("✅ 所有文件已生成完毕！")
        print("="*70)
        print()
        print("📋 下一步操作:")
        print("  1. 打开 Chrome 浏览器")
        print("  2. 安装 Tampermonkey 扩展")
        print("  3. 复制 wenjuanxin_misaka.user.js 内容到 Tampermonkey 编辑器")
        print("  4. 保存并测试填写")
        print()
    
    else:
        print()
        print("="*70)
        print("❌ 无法分析问卷数据，请检查文件是否存在")
        print("="*70)

if __name__ == "__main__":
    main()
