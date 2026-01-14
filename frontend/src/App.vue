<script setup>
import { ref, computed } from 'vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true // 将换行符转换为 <br>
})

const file = ref(null)
const content = ref('')
const loading = ref(false)
const error = ref('')
const fileName = ref('')

// 计算属性：将 Markdown 内容转换为 HTML
const parsedContent = computed(() => {
  if (!content.value) return ''
  return md.render(content.value)
})

const handleFileChange = (event) => {
  const selectedFile = event.target.files[0]
  if (selectedFile) {
    processFile(selectedFile)
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  const droppedFile = event.dataTransfer.files[0]
  if (droppedFile) {
    processFile(droppedFile)
  }
}

const processFile = (selectedFile) => {
  file.value = selectedFile
  fileName.value = selectedFile.name
  error.value = ''
  content.value = ''
  uploadFile()
}

const uploadFile = async () => {
  if (!file.value) return

  loading.value = true
  error.value = ''

  const formData = new FormData()
  formData.append('file', file.value)

  try {
    const response = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`上传失败: ${response.statusText}`)
    }

    const data = await response.json()
    content.value = data.content
  } catch (err) {
    console.error(err)
    error.value = '上传或处理文件时发生错误: ' + err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen font-sans text-gray-800">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
      <!-- 头部导航 -->
      <header class="mb-8">
        <div class="flex justify-between items-center">
          <div class="flex items-center space-x-3">
            <div class="bg-primary p-2 rounded-lg text-white">
              <i class="fa fa-file-text-o text-xl"></i>
            </div>
            <h1 class="text-2xl md:text-3xl font-bold text-gradient">文件查看器</h1>
          </div>
          <div class="hidden md:flex items-center space-x-4">
            <button class="p-2 rounded-full hover:bg-gray-200 transition-all">
              <i class="fa fa-moon-o text-gray-600"></i>
            </button>
            <button class="p-2 rounded-full hover:bg-gray-200 transition-all">
              <i class="fa fa-question-circle text-gray-600"></i>
            </button>
          </div>
        </div>
      </header>

      <!-- 主要内容区域 -->
      <main class="space-y-8">
        <!-- 文件上传区域 -->
        <section class="bg-white rounded-2xl shadow-md overflow-hidden">
          <div class="p-6 md:p-8">
            <h2 class="text-xl md:text-2xl font-semibold mb-6 flex items-center">
              <i class="fa fa-cloud-upload text-primary mr-3"></i>
              上传文件
            </h2>
            
            <!-- 上传区域 -->
            <div 
              class="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-primary transition-all duration-300 relative"
              @dragover.prevent
              @drop="handleDrop"
            >
              <input 
                type="file" 
                class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                @change="handleFileChange" 
              />
              <div class="upload-content">
                <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 text-primary mb-4">
                  <i class="fa fa-file-o text-3xl"></i>
                </div>
                <h3 class="text-lg font-medium mb-2">拖放文件到此处</h3>
                <p class="text-gray-500 mb-4">或者</p>
                <label class="inline-block px-6 py-3 bg-primary text-white rounded-lg hover:bg-blue-600 transition-all cursor-pointer shadow-hover">
                  <span>选择文件</span>
                </label>
              </div>
            </div>

            <!-- 文件名显示 -->
            <div v-if="fileName" class="mt-4 text-center text-gray-700 font-medium">
              已选择: {{ fileName }}
            </div>
            
            <!-- 错误信息 -->
            <div v-if="error" class="mt-4 p-4 bg-red-50 text-red-600 rounded-lg border border-red-200">
              <i class="fa fa-exclamation-circle mr-2"></i>
              {{ error }}
            </div>
          </div>
        </section>

        <!-- 内容显示区域 -->
        <section v-if="loading || content" class="bg-white rounded-2xl shadow-md overflow-hidden transition-all-300">
          <div class="p-6 md:p-8">
            <h2 class="text-xl md:text-2xl font-semibold mb-6 flex items-center justify-between">
              <div class="flex items-center">
                <i class="fa fa-file-text text-primary mr-3"></i>
                文件内容
              </div>
              <div v-if="loading" class="text-sm text-gray-500 flex items-center">
                <i class="fa fa-spinner fa-spin mr-2"></i> 处理中...
              </div>
            </h2>

            <div v-if="loading" class="animate-pulse space-y-4">
              <div class="h-4 bg-gray-200 rounded w-3/4"></div>
              <div class="h-4 bg-gray-200 rounded w-1/2"></div>
              <div class="h-4 bg-gray-200 rounded w-5/6"></div>
              <div class="h-4 bg-gray-200 rounded w-full"></div>
            </div>

            <div v-else class="bg-gray-50 rounded-xl p-6 border border-gray-200 overflow-x-auto">
              <!-- 使用 v-html 渲染 Markdown 转换后的 HTML -->
              <div class="prose prose-sm md:prose-base lg:prose-lg max-w-none text-gray-800" v-html="parsedContent"></div>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<style>
/* Markdown 样式增强 */
.prose table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1.25em;
  margin-bottom: 1.25em;
  font-size: 0.875em;
  line-height: 1.7142857;
}

.prose thead th {
  padding-right: 0.5714286em;
  padding-bottom: 0.5714286em;
  padding-left: 0.5714286em;
  font-weight: 600;
  color: #111827;
  text-align: left;
  border-bottom-width: 1px;
  border-bottom-color: #d1d5db;
  white-space: nowrap;
}

.prose tbody td {
  padding: 0.5714286em;
  vertical-align: top;
  border-bottom-width: 1px;
  border-bottom-color: #e5e7eb;
}

.prose tbody tr:nth-child(even) {
  background-color: #f9fafb;
}

.prose h1, .prose h2, .prose h3 {
  color: #111827;
  font-weight: 600;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}

.prose h1 { font-size: 2.25em; }
.prose h2 { font-size: 1.5em; border-bottom: 1px solid #e5e7eb; padding-bottom: 0.3em; }
.prose h3 { font-size: 1.25em; }

.prose p {
  margin-top: 1.25em;
  margin-bottom: 1.25em;
}

.prose ul {
  list-style-type: disc;
  padding-left: 1.625em;
  margin-top: 1.25em;
  margin-bottom: 1.25em;
}

.prose ol {
  list-style-type: decimal;
  padding-left: 1.625em;
  margin-top: 1.25em;
  margin-bottom: 1.25em;
}

.prose pre {
  background-color: #1f2937;
  color: #e5e7eb;
  padding: 1em;
  border-radius: 0.375rem;
  overflow-x: auto;
}

.prose code {
  color: #111827;
  font-weight: 600;
  font-size: 0.875em;
  background-color: #f3f4f6;
  padding: 0.25em 0.4em;
  border-radius: 0.25rem;
}

.prose pre code {
  background-color: transparent;
  color: inherit;
  font-size: 1em;
  font-weight: 400;
  padding: 0;
}
</style>
