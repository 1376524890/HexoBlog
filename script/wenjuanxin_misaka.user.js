// ==UserScript==
// @name         问卷星自动填写 - 御坂妹妹定制版
// @version      1.0
// @description 全自动填写问卷星，基于 WenjuanXin 优化，支持自定义答案配置
// @author       御坂妹妹 11 号
// @namespace    http://tampermonkey.net/
// @match        https://www.wjx.cn/jq/*.aspx
// @match        https://www.wjx.cn/m/*.aspx
// @match        https://www.wjx.cn/hj/*.aspx
// @match        https://v.wjx.cn/vm/*.aspx
// @require      https://greasyfork.org/scripts/438455-wenjuanxin-tampermonkey-code/files/wenjuanxin.user.js
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
        
        // 示例：第 1 题是填空题，问"您的年龄"
        // { id: 1, answer: ["18 岁以下", "18-25 岁", "26-35 岁", "36-45 岁", "46-55 岁", "56 岁以上"] },
        
        // 示例：第 2 题是填空题，问"您的性别"
        // { id: 2, answer: ["男", "女", "不愿透露"] },
        
        // 如果有其他填空题，继续添加...
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
                    console.log("✓ 单选（带图）已选择");
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
                        console.log("✓ 单选已选择");
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
                console.log("✓ 多选题已选择");
            } catch (e) {
                console.log("⚠ 多选填写失败:", e.message);
            }
        };

        // 表格单选
        this.matrixSingleChoose = function(subject) {
            try {
                var tr = subject.querySelectorAll("tbody > tr");
                for (var i = 0; i < tr.length; i++) {
                    var td = tr[i].querySelectorAll("td");
                    if (td.length > 0) {
                        td[randint(0, td.length - 1)].click();
                    }
                }
                console.log("✓ 表格单选已选择");
            } catch (e) {
                console.log("⚠ 表格单选填写失败:", e.message);
            }
        };

        // 表格多选
        this.matrixMultiChoose = function(subject) {
            try {
                var tr = subject.querySelectorAll("tbody > tr");
                for (var i = 0; i < tr.length; i++) {
                    var td = tr[i].querySelectorAll("td");
                    for (var j = 0; j < td.length; j++) {
                        td[j].querySelectorAll("input")[0].checked = false;
                    }
                    var times = randint(1, Math.max(1, td.length - 1));
                    for (var k = 0; k < times; k++) {
                        var randomChoose = td.splice(randint(0, td.length - 1), 1)[0];
                        if (randomChoose.querySelectorAll("input")[0]) {
                            randomChoose.querySelectorAll("input")[0].checked = true;
                        }
                    }
                }
                console.log("✓ 表格多选已选择");
            } catch (e) {
                console.log("⚠ 表格多选填写失败:", e.message);
            }
        };

        // 星星评分
        this.star = function(subject) {
            try {
                var list = subject.querySelectorAll("li:not([class='notchoice'])");
                if (list.length > 0) {
                    list[randint(0, list.length - 1)].click();
                    console.log("✓ 星星评分已选择");
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
                    console.log("✓ 下拉已选择");
                }
            } catch (e) {
                console.log("⚠ 下拉选择填写失败:", e.message);
            }
        };

        // 拉条选择
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
                    console.log("✓ 拉条已选择");
                }
            } catch (e) {
                console.log("⚠ 拉条填写失败:", e.message);
            }
        };

        // 排序题
        this.sort = function(subject) {
            try {
                var list = subject.querySelectorAll("li");
                for (var i = 0; i < list.length; i++) {
                    var input = list[i].querySelectorAll("input")[0];
                    if (input) input.checked = false;
                }
                var arr = Array.from(list);
                arr.sort(() => Math.random() - 0.5);
                for (var i = 0; i < list.length; i++) {
                    if (arr[i].querySelectorAll("input")[0]) {
                        arr[i].querySelectorAll("input")[0].checked = true;
                    }
                }
                console.log("✓ 排序已选择");
            } catch (e) {
                console.log("⚠ 排序填写失败:", e.message);
            }
        };
    }

    // ============================================================
    // 🎯 智慧树题目类型判断
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
                        console.log(`  [${i+1}] 单选题`);
                        rc.singleChoose(q[i]);
                    } else if (input[0].type == 'checkbox') {
                        console.log(`  [${i+1}] 多选题`);
                        rc.multiChoose(q[i]);
                    }
                }
                // 表格
                else if (q[i].querySelectorAll("table")[0]) {
                    var inputs = q[i].querySelectorAll("input");
                    if (inputs.length > 0 && inputs[0].type == 'radio') {
                        console.log(`  [${i+1}] 表格单选`);
                        rc.matrixSingleChoose(q[i]);
                    } else if (inputs.length > 0 && inputs[0].type == 'checkbox') {
                        console.log(`  [${i+1}] 表格多选`);
                        rc.matrixMultiChoose(q[i]);
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
                    console.log(`  [${i+1}] 星星评分`);
                    rc.star(q[i]);
                }
                // 下拉选择
                else if (q[i].querySelectorAll("select")[0]) {
                    console.log(`  [${i+1}] 下拉选择`);
                    rc.dropdownSelect(q[i]);
                }
                // 拉条
                else if (q[i].querySelectorAll(".slider")[0]) {
                    console.log(`  [${i+1}] 拉条`);
                    rc.slider(q[i]);
                }
                // 排序
                else if (q[i].querySelectorAll(".lisort")[0]) {
                    console.log(`  [${i+1}] 排序题`);
                    rc.sort(q[i]);
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
    
    // 延迟执行，确保页面完全加载
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
                console.log("✓ 已滚动到提交按钮");
            }
        } catch (e) {
            console.log("⚠ 滚动失败:", e.message);
        }
        
        // 2 秒后提交
        setTimeout(function() {
            try {
                var submitBtn = document.getElementById("submit_button");
                if (submitBtn) {
                    submitBtn.click();
                    console.log("✅ 问卷已提交！");
                }
            } catch (e) {
                console.log("⚠ 提交失败:", e.message);
            }
        }, 2000);
        
        // 5 秒后刷新（自动跳转下一份）
        setTimeout(function() {
            try {
                var currentURL = window.location.href;
                var pat = /complete\.aspx\?activityid=(\d+)/;
                var obj = pat.exec(currentURL);
                
                if (obj) {
                    // 如果有下一个问卷，跳转到下一个
                    var nextURL = "https://www.wjx.cn/jq/" + obj[1] + ".aspx";
                    window.location.href = nextURL;
                    console.log("✓ 已跳转到下一份问卷");
                } else {
                    // 否则刷新当前页面
                    location.reload();
                    console.log("✓ 已刷新页面");
                }
            } catch (e) {
                console.log("⚠ 自动跳转失败，尝试刷新:", e.message);
                location.reload();
            }
        }, 5000);
        
    }, 1000);

    // 阻止默认弹窗
    window.alert = function(str) {
        console.log("⚠ 弹窗被阻止:", str);
        return;
    };

})();
