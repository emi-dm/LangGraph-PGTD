# Informe general: Segmentación automática 3D de imágenes médicas (2019-2024)

## Introducción
La segmentación automática de imágenes médicas tridimensionales (3D) es un área clave en el procesamiento de imágenes biomédicas, con aplicaciones en diagnóstico, planificación quirúrgica y radioterapia. El avance de técnicas de deep learning ha impulsado el desarrollo de métodos cada vez más precisos y robustos para segmentar órganos, tumores y otras estructuras anatómicas en volúmenes obtenidos por MRI, CT, PET, entre otros.

## Estado del arte y tendencias metodológicas
- **Deep learning 3D:** Las arquitecturas como 3D U-Net y V-Net dominan el campo, permitiendo la segmentación directa de volúmenes completos. Los transformers y modelos híbridos (combinando CNNs y atención) emergen como alternativas para capturar dependencias espaciales de largo alcance.
- **Métodos 2D, 2.5D y 3D:** Aunque los modelos 3D suelen ofrecer mayor precisión, los métodos 2.5D (multi-view, multi-slice, fusión de features) y 2D siguen siendo relevantes por su menor coste computacional y robustez en imágenes anisotrópicas.
- **Transfer learning y aprendizaje semi/auto-supervisado:** Se exploran para superar la escasez de datos anotados y mejorar la generalización.

## Comparación de enfoques
- **3D U-Net:** Referente en segmentación volumétrica, especialmente en conjuntos de datos bien anotados y con resolución isotrópica.
- **Transformers:** Mejoran la captura de contexto global, especialmente en tareas multimodales o con estructuras complejas.
- **Métodos híbridos y 2.5D:** Ofrecen buen compromiso entre precisión y eficiencia, útiles en escenarios clínicos con recursos limitados.

## Aplicaciones clínicas principales
- **Neuroimagen:** Segmentación de tumores cerebrales, ventrículos y estructuras corticales.
- **Oncología:** Delineación de tumores y órganos en riesgo para radioterapia.
- **Cardiología:** Segmentación de cavidades cardíacas y vasos.
- **Abdomen:** Segmentación de hígado, bazo, riñones y páncreas.

## Evaluación de desempeño
- **Métricas:** Dice, IoU, Hausdorff Distance (95HD) son los estándares para comparar métodos.
- **Resultados:** 3D U-Net y variantes logran los mejores resultados en la mayoría de benchmarks, aunque los métodos 2.5D y transformers muestran competitividad en ciertos escenarios.

## Ventajas y limitaciones
- **Ventajas:** Mayor precisión volumétrica, automatización, potencial para integración clínica.
- **Limitaciones:** Alto coste computacional, necesidad de grandes volúmenes de datos anotados, sensibilidad a la variabilidad inter-escáner y artefactos.

## Perspectivas futuras
- Integración de modelos multimodales y universales.
- Mayor uso de aprendizaje auto-supervisado y transfer learning.
- Desarrollo de soluciones eficientes para entornos clínicos con recursos limitados.

## Referencias
1. Bai, F., Du, Y., Huang, T., et al. (2024). M3D: Advancing 3D Medical Image Analysis with Multi-Modal Large Language Models. arXiv:2404.00578.
2. Chen, T., Wang, C., Chen, Z., et al. (2024). HiDiff: Hybrid Diffusion Framework for Medical Image Segmentation. arXiv:2407.03548.
3. Messaoudi, H., Belaid, A., Ben Salem, D., et al. (2023). Cross-dimensional transfer learning in medical image segmentation with deep learning. arXiv:2307.15872.
4. Zhang, Y., Liao, Q., Ding, L., et al. (2020). Bridging 2D and 3D Segmentation Networks for Computation Efficient Volumetric Medical Image Segmentation: An Empirical Study of 2.5D Solutions. arXiv:2010.06163.
5. Chen, J., Frey, E. C., He, Y., et al. (2021). TransMorph: Transformer for unsupervised medical image registration. arXiv:2111.10480.
