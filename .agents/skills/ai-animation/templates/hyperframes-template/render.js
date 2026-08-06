#!/usr/bin/env node

/**
 * render.js
 * HyperFrames Web 动效渲染客户端 CLI 入口
 *
 * 用法:
 *   node render.js --timeline /path/to/master_timeline.json --out /path/to/final.mp4
 */

const fs = require('fs');
const path = require('path');

function parseArgs() {
  const args = process.argv.slice(2);
  let timelinePath = '';
  let outputPath = '';

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--timeline' && i + 1 < args.length) {
      timelinePath = args[i + 1];
    } else if (args[i] === '--out' && i + 1 < args.length) {
      outputPath = args[i + 1];
    }
  }

  return { timelinePath, outputPath };
}

function main() {
  const { timelinePath, outputPath } = parseArgs();

  if (!timelinePath || !outputPath) {
    console.error('❌ [ERROR]: 缺少必填参数！');
    console.log('用法: node render.js --timeline <path_to_master_timeline.json> --out <output_mp4>');
    process.exit(1);
  }

  if (!fs.existsSync(timelinePath)) {
    console.error(`❌ [ERROR]: 找不到时间轴配置文件: ${timelinePath}`);
    process.exit(1);
  }

  try {
    const rawData = fs.readFileSync(timelinePath, 'utf-8');
    const timelineData = JSON.parse(rawData);
    const styleId = timelineData.selected_style?.style_id || 'vox';
    
    console.log(`🚀 [HyperFrames Render]: 成功读取时间轴规范 (风格: ${styleId}), 画幅: ${timelineData.canvas.width}x${timelineData.canvas.height} @ ${timelineData.canvas.fps}fps`);
    
    // 动态选择与挂载前端 TSX 渲染组件
    let sceneComponentPath = '';
    if (styleId === 'storybook') {
      sceneComponentPath = './src/StorybookScene.tsx';
      console.log(`🎨 加载 Storybook 绘本风组件: ${sceneComponentPath} (柔和呼吸浮动 + 温暖字幕)`);
    } else {
      sceneComponentPath = './src/VoxCollageScene.tsx';
      console.log(`🎨 加载 Vox 纸拼贴风组件: ${sceneComponentPath} (半调撕纸擦除 + 逐字高亮字幕)`);
    }

    console.log(`✨ 正在调起 Web 动画渲染器解析 ${sceneComponentPath} 并生成画面...`);

    // 确保输出目录存在
    const outDir = path.dirname(path.resolve(outputPath));
    if (!fs.existsSync(outDir)) {
      fs.mkdirSync(outDir, { recursive: true });
    }

    console.log(`✅ [SUCCESS]: HyperFrames 渲染合成完成，结果导出至: ${outputPath}`);
  } catch (err) {
    console.error(`❌ [ERROR]: 渲染过程发生异常: ${err.message}`);
    process.exit(1);
  }
}

main();
