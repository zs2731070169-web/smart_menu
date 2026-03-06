<template>
  <section class="menu-section">
    <div class="section-header">
      <h2 class="section-title">
        <span class="title-icon">🍽</span>
        今日菜单
      </h2>
      <span v-if="menus.length" class="menu-count">{{ menus.length }} 道菜品</span>
    </div>

    <!-- 加载骨架屏 -->
    <div v-if="loading" class="menu-grid">
      <div v-for="i in 6" :key="i" class="menu-card skeleton-card">
        <div class="skeleton" style="height:18px;width:70%;margin-bottom:8px"></div>
        <div class="skeleton" style="height:14px;width:40%;margin-bottom:6px"></div>
        <div class="skeleton" style="height:12px;width:90%"></div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="empty-state">
      <span class="empty-icon">⚠️</span>
      <p>{{ error }}</p>
      <button class="retry-btn" @click="$emit('retry')">重新加载</button>
    </div>

    <!-- 菜单网格 -->
    <div v-else class="menu-grid">
      <div
          v-for="item in menus"
          :key="item.id"
          class="menu-card"
          :class="{
          'recommended': highlightIds.includes(String(item.id)),
          'unavailable': !item.is_available
        }"
      >
        <!-- 推荐角标 -->
        <div v-if="highlightIds.includes(String(item.id))" class="recommend-badge">
          推荐
        </div>

        <div class="card-header">
          <h3 class="dish-name">{{ item.dish_name }}</h3>
          <span class="price">¥{{ item.price }}</span>
        </div>

        <div class="card-tags">
          <span class="tag tag-category">{{ item.category }}</span>
          <span v-if="item.is_vegetarian" class="tag tag-veg">素食</span>
          <span v-if="item.spice_level && item.spice_level !== '不辣'" class="tag tag-spice">
            {{ item.spice_level }}
          </span>
        </div>

        <p class="dish-desc">{{ item.description }}</p>

        <div class="card-footer">
          <span class="ingredient-hint">{{ item.main_ingredients }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  menus: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
  error: String,
  highlightIds: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['retry'])
</script>

<style scoped>
.menu-section {
  padding: 0 16px 100px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.title-icon {
  font-size: 20px;
}

.menu-count {
  font-size: 12px;
  color: var(--text-light);
  background: var(--border);
  padding: 2px 8px;
  border-radius: 10px;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.menu-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 14px 12px;
  border: 2px solid transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  animation: fadeIn 0.3s ease both;
}

.menu-card.recommended {
  border-color: var(--primary);
  box-shadow: 0 4px 16px var(--shadow);
  background: linear-gradient(135deg, #fff 0%, #fff8f5 100%);
  animation: pulse 0.4s ease;
}

.menu-card.unavailable {
  opacity: 0.5;
  filter: grayscale(0.3);
}

.recommend-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 3px 8px;
  border-bottom-left-radius: 8px;
  letter-spacing: 0.5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 6px;
  margin-bottom: 8px;
}

.dish-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
  flex: 1;
}

.price {
  font-size: 15px;
  font-weight: 800;
  color: var(--primary);
  white-space: nowrap;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 6px;
  font-weight: 500;
}

.tag-category {
  background: #FFF0E8;
  color: var(--primary-dark);
}

.tag-veg {
  background: #E8F8EE;
  color: #27AE60;
}

.tag-spice {
  background: #FFF0F0;
  color: var(--secondary);
}

.dish-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 8px;
}

.card-footer {
  border-top: 1px solid var(--border);
  padding-top: 6px;
}

.ingredient-hint {
  font-size: 11px;
  color: var(--text-light);
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

.skeleton-card {
  height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 16px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 40px;
  display: block;
  margin-bottom: 12px;
}

.retry-btn {
  margin-top: 12px;
  padding: 8px 20px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
}

/* gap fallback for older Android WebView */
@supports not (gap: 1rem) {
  .section-title > * + * {
    margin-left: 6px;
  }

  .card-header > * + * {
    margin-left: 6px;
  }
}

@media (max-width: 390px) {
  .menu-section {
    padding: 0 14px 100px;
  }

  .section-header {
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 6px;
  }

  .menu-grid {
    gap: 10px;
  }

  .menu-card {
    padding: 12px 10px;
  }

  .dish-name,
  .price {
    font-size: 14px;
  }
}

@media (max-width: 350px) {
  .menu-grid {
    grid-template-columns: 1fr;
  }
}
</style>
