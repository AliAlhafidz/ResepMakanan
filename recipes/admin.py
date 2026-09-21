from django.contrib import admin
from .models import Category, Tag, Recipe, Ingredient, InstructionStep, RecipeNutrition, Favorite, MealPlan, ShoppingListItem

class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1
    fields = ('sort_order', 'amount', 'unit', 'item_name', 'notes')

class InstructionStepInline(admin.StackedInline):
    model = InstructionStep
    extra = 1
    fields = ('step_number', 'instruction', 'step_image')

class RecipeNutritionInline(admin.StackedInline):
    model = RecipeNutrition
    can_delete = False
    max_num = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_name')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'difficulty', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'is_featured', 'difficulty', 'category')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    inlines = [IngredientInline, InstructionStepInline, RecipeNutritionInline]
    actions = ['make_published', 'make_featured', 'unmake_featured']

    @admin.action(description='Setujui dan Publikasikan Resep terpilih')
    def make_published(self, request, queryset):
        queryset.update(status=Recipe.Status.PUBLISHED, rejection_reason="")

    @admin.action(description='Tandai sebagai Menu Hari Ini')
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description='Cabut dari Menu Hari Ini')
    def unmake_featured(self, request, queryset):
        queryset.update(is_featured=False)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created_at')
    search_fields = ('user__username', 'recipe__title')

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'plan_date', 'meal_time')
    list_filter = ('meal_time', 'plan_date')

@admin.register(ShoppingListItem)
class ShoppingListItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'amount', 'unit', 'user', 'is_checked')
    list_filter = ('is_checked',)
