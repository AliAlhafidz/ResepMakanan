import re
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import Recipe, Ingredient, InstructionStep, RecipeNutrition, validate_image_file

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'title', 'category', 'tags', 'description', 'image',
            'default_servings', 'prep_time_minutes', 'cook_time_minutes', 'difficulty'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none text-stone-800 bg-surface-50',
                'placeholder': 'Contoh: Rendang Sapi Padang Asli'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none text-stone-800 bg-surface-50'
            }),
            'tags': forms.CheckboxSelectMultiple(),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none text-stone-800 bg-surface-50',
                'placeholder': 'Ceritakan keistimewaan rasa atau asal-usul resep ini...'
            }),
            'default_servings': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none text-stone-800 bg-surface-50',
                'min': '1'
            }),
            'prep_time_minutes': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none text-stone-800 bg-surface-50',
                'min': '1'
            }),
            'cook_time_minutes': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none text-stone-800 bg-surface-50',
                'min': '1'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 outline-none text-stone-800 bg-surface-50'
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not re.search(r'[a-zA-Z0-9]', title):
            raise ValidationError("Judul resep wajib mengandung minimal satu karakter alfanumerik (huruf atau angka).")
        return title

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            validate_image_file(image)
        return image


class RecipeNutritionForm(forms.ModelForm):
    class Meta:
        model = RecipeNutrition
        fields = ['calories', 'protein_grams', 'carbs_grams', 'fat_grams']
        widgets = {
            'calories': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 rounded-xl border border-stone-300 focus:border-primary-600 outline-none text-sm bg-surface-50',
                'placeholder': 'Kkal'
            }),
            'protein_grams': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 rounded-xl border border-stone-300 focus:border-primary-600 outline-none text-sm bg-surface-50',
                'placeholder': 'g', 'step': '0.1'
            }),
            'carbs_grams': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 rounded-xl border border-stone-300 focus:border-primary-600 outline-none text-sm bg-surface-50',
                'placeholder': 'g', 'step': '0.1'
            }),
            'fat_grams': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 rounded-xl border border-stone-300 focus:border-primary-600 outline-none text-sm bg-surface-50',
                'placeholder': 'g', 'step': '0.1'
            }),
        }


class BaseIngredientFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        valid_items_count = 0
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            item_name = form.cleaned_data.get('item_name')
            if item_name:
                valid_items_count += 1
        if valid_items_count < 1:
            raise ValidationError("Resep wajib memiliki minimal 1 bahan masakan.")


class BaseInstructionStepFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        valid_steps = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            instruction = form.cleaned_data.get('instruction')
            if instruction:
                valid_steps.append(form)
        if len(valid_steps) < 1:
            raise ValidationError("Resep wajib memiliki minimal 1 langkah instruksi memasak.")

    def save(self, commit=True):
        instances = super().save(commit=False)
        # Urutkan ulang step_number berurutan 1, 2, 3...
        step_number = 1
        for instance in instances:
            instance.step_number = step_number
            step_number += 1
            if commit:
                instance.save()
        return instances


IngredientFormSet = inlineformset_factory(
    Recipe,
    Ingredient,
    formset=BaseIngredientFormSet,
    fields=['sort_order', 'amount', 'unit', 'item_name', 'notes'],
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
    widgets={
        'sort_order': forms.NumberInput(attrs={'class': 'w-14 px-2 py-1.5 rounded-lg border border-stone-300 text-sm text-center'}),
        'amount': forms.NumberInput(attrs={'class': 'w-24 px-3 py-1.5 rounded-lg border border-stone-300 text-sm', 'placeholder': '500', 'step': 'any', 'min': '0'}),
        'unit': forms.TextInput(attrs={'class': 'w-24 px-3 py-1.5 rounded-lg border border-stone-300 text-sm', 'placeholder': 'gram'}),
        'item_name': forms.TextInput(attrs={'class': 'flex-1 px-3 py-1.5 rounded-lg border border-stone-300 text-sm', 'placeholder': 'Daging sapi'}),
        'notes': forms.TextInput(attrs={'class': 'w-32 px-3 py-1.5 rounded-lg border border-stone-300 text-sm', 'placeholder': 'potong dadu'}),
    }
)

InstructionStepFormSet = inlineformset_factory(
    Recipe,
    InstructionStep,
    formset=BaseInstructionStepFormSet,
    fields=['step_number', 'instruction', 'step_image'],
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
    widgets={
        'step_number': forms.NumberInput(attrs={'class': 'w-14 px-2 py-1.5 rounded-lg border border-stone-300 text-sm text-center', 'min': '1'}),
        'instruction': forms.Textarea(attrs={'rows': 2, 'class': 'flex-1 px-3 py-1.5 rounded-lg border border-stone-300 text-sm', 'placeholder': 'Jelaskan instruksi memasak...'}),
        'step_image': forms.FileInput(attrs={'class': 'text-xs text-stone-500 file:mr-2 file:py-1 file:px-3 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-stone-100 file:text-stone-700 hover:file:bg-stone-200'}),
    }
)
