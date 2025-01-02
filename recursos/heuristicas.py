import pandas as pd
from typing import List, Any, Dict

def reduccion_destinosXcobertura(list_destinos):
    """
    Aplica una heurística de reducción al conjunto de destinos.

    Si el inventario en un destino permite un tiempo de cobertura real superior
    al tiempo de cobertura planificado, dicho destino se excluye del análisis.

    Además, si la lista resultante de destinos es vacía, la función indica
    que un algoritmo externo debe detenerse devolviendo "Stop".
    En caso contrario, devuelve "Continue" junto con la nueva lista.

    Args:
        list_destinos (list): Lista de objetos de tipo Destino.

    Returns:
        tuple: Una tupla con dos elementos:
            - list: Nueva lista con los destinos que cumplen la condición de reducción.
            - str: "Stop" si la lista resultante está vacía, "Continue" en caso contrario.

    Raises:
        ValueError: Si `list_destinos` no es una lista.
    """
    if not isinstance(list_destinos, list):
        raise ValueError("El argumento `list_destinos` debe ser una lista.")

    # Usamos list comprehension para mejorar la legibilidad
    new_list = [
        destino for destino in list_destinos
        if destino.get_tiempo_cobertura() < destino.tiempo_cobertura_plan
    ]

    # Determinamos si se debe detener el algoritmo externo
    if len(new_list) == 0:
        return (new_list, "Stop")
    else:
        return (new_list, "Continue")


def reduccion_destinosXvehiculos(list_destinos, list_vehiculos):
    """
    Aplica una reducción del conjunto de destinos en función del número de vehículos disponibles.

    Si el número de vehículos es menor que el número de destinos, selecciona un subconjunto 
    de destinos ordenados ascendentemente por su tiempo de cobertura real, con un tamaño igual 
    al número de vehículos. En caso contrario, devuelve todos los destinos.

    Args:
        list_destinos (list): Lista de objetos de tipo Destino.
        list_vehiculos (list): Lista de objetos de tipo Vehículo.

    Returns:
        list: Lista de destinos seleccionados tras aplicar la reducción.

    Raises:
        ValueError: Si `list_destinos` o `list_vehiculos` no son listas, o si están vacías.
        AttributeError: Si los objetos de `list_destinos` no tienen los atributos `identif` y `tiempo_cobertura`.
    """
    # Validaciones de entrada
    if not isinstance(list_destinos, list) or not isinstance(list_vehiculos, list):
        raise ValueError("Ambos argumentos deben ser listas.")
    if len(list_destinos) == 0 or len(list_vehiculos) == 0:
        raise ValueError("Las listas no pueden estar vacías.")
    
    # Validación de atributos necesarios en los destinos
    for destino in list_destinos:
        if not hasattr(destino, "identif") or not hasattr(destino, "tiempo_cobertura"):
            raise AttributeError("Los objetos en `list_destinos` deben tener los atributos `identif` y `tiempo_cobertura`.")
    
    # Caso en el que hay más destinos que vehículos
    if len(list_vehiculos) < len(list_destinos):
        # Crear DataFrame para ordenar por tiempo de cobertura
        data = {
            'ID': [destino.identif for destino in list_destinos],
            'Cobertura': [destino.tiempo_cobertura for destino in list_destinos]
        }
        df_cobertura_destinos = pd.DataFrame(data)
        df_cobertura_destinos.sort_values(by='Cobertura', inplace=True)

        # Seleccionar los IDs top según el número de vehículos
        top_ids = df_cobertura_destinos['ID'].iloc[:len(list_vehiculos)].values

        # Filtrar destinos cuyo ID esté en los seleccionados
        new_list_destinos = [destino for destino in list_destinos if destino.identif in top_ids]
        return new_list_destinos
    else:
        # Caso en el que el número de vehículos es suficiente
        return list_destinos

def determinar_cant_mercancias_vehiculosXdestino(list_vehiculos, list_destinos):
    """
    Determina la cantidad de mercancías a transportar desde cada vehículo hacia cada destino.

    Compara la carga de cada vehículo con la demanda de cada destino. Si la carga del vehículo es mayor 
    que la demanda del destino, se descarga únicamente la demanda. En caso contrario, se descarga toda 
    la carga del vehículo.

    Args:
        list_vehiculos (list): Lista de objetos de tipo Vehículo.
        list_destinos (list): Lista de objetos de tipo Destino.

    Returns:
        dict: Diccionario con las combinaciones de vehículo y destino como claves (tuplas) y las cantidades 
        de mercancías a transportar como valores.

    Raises:
        ValueError: Si `list_vehiculos` o `list_destinos` no son listas, o si están vacías.
        AttributeError: Si los objetos en las listas no tienen los métodos `get_carga` o `get_demanda`.
    """
    # Validaciones de entrada
    if not isinstance(list_vehiculos, list) or not isinstance(list_destinos, list):
        raise ValueError("Ambos argumentos deben ser listas.")
    if len(list_vehiculos) == 0 or len(list_destinos) == 0:
        raise ValueError("Las listas no pueden estar vacías.")
    
    # Validación de atributos necesarios
    for veh in list_vehiculos:
        if not hasattr(veh, "get_carga") or not hasattr(veh, "identif"):
            raise AttributeError("Los objetos en `list_vehiculos` deben tener los métodos `get_carga` y el atributo `identif`.")
    for destino in list_destinos:
        if not hasattr(destino, "get_demanda") or not hasattr(destino, "identif"):
            raise AttributeError("Los objetos en `list_destinos` deben tener los métodos `get_demanda` y el atributo `identif`.")

    # Diccionario para almacenar las cantidades transportadas
    params_carga_transp = {}

    # Comparar la carga del vehículo con la demanda del destino
    for veh in list_vehiculos:
        for destino in list_destinos:
            carga_disponible = veh.get_carga()
            demanda_destino = destino.get_demanda()

            # Determinar la cantidad a transportar
            if carga_disponible > demanda_destino:
                params_carga_transp[(veh.identif, destino.identif)] = demanda_destino
            else:
                params_carga_transp[(veh.identif, destino.identif)] = carga_disponible

    return params_carga_transp
def determinar_indicador_trafico(list_vehiculos, list_destinos, matrix_distancias, params_carga_transportada):
    """
    Calcula el indicador de tráfico de mercancías para cada combinación de vehículo y destino.

    El tráfico de mercancías se calcula dividiendo la cantidad de carga a transportar desde cada 
    vehículo hacia cada destino entre la distancia desde la posición actual del vehículo hasta 
    la ubicación del destino.

    Args:
        list_vehiculos (list): Lista de objetos de tipo Vehículo.
        list_destinos (list): Lista de objetos de tipo Destino.
        matrix_distancias (dict): Diccionario que representa las distancias entre posiciones, con claves como tuplas (origen, destino).
        params_carga_transportada (dict): Diccionario con las cantidades de carga a transportar, 
            con claves como tuplas (identif_vehiculo, identif_destino) y valores numéricos.

    Returns:
        dict: Diccionario con el indicador de tráfico de mercancías para cada combinación de vehículo y destino.
              Las claves son tuplas (identif_vehiculo, identif_destino), y los valores son los indicadores calculados.

    Raises:
        ValueError: Si alguna de las listas está vacía o `matrix_distancias` o `params_carga_transportada` no son diccionarios.
        KeyError: Si faltan claves necesarias en `matrix_distancias` o `params_carga_transportada`.
        ZeroDivisionError: Si alguna distancia en `matrix_distancias` es 0.
        AttributeError: Si los objetos en `list_vehiculos` o `list_destinos` no tienen los atributos necesarios.
    """
    # Validaciones de entrada
    if not isinstance(list_vehiculos, list) or not isinstance(list_destinos, list):
        raise ValueError("`list_vehiculos` y `list_destinos` deben ser listas.")
    if not isinstance(matrix_distancias, dict) or not isinstance(params_carga_transportada, dict):
        raise ValueError("`matrix_distancias` y `params_carga_transportada` deben ser diccionarios.")
    if len(list_vehiculos) == 0 or len(list_destinos) == 0:
        raise ValueError("`list_vehiculos` y `list_destinos` no pueden estar vacías.")
    
    # Validación de atributos necesarios en los vehículos y destinos
    for veh in list_vehiculos:
        if not hasattr(veh, "get_posicion") or not hasattr(veh, "identif"):
            raise AttributeError("Los objetos en `list_vehiculos` deben tener los métodos `get_posicion` y el atributo `identif`.")
    for destino in list_destinos:
        if not hasattr(destino, "identif"):
            raise AttributeError("Los objetos en `list_destinos` deben tener el atributo `identif`.")

    # Calcular el indicador de tráfico de mercancías
    params_ind_trafico = {}
    for veh in list_vehiculos:
        for destino in list_destinos:
            veh_id = veh.identif
            destino_id = destino.identif
            veh_pos = veh.get_posicion()
            
            # Verificar que las claves necesarias existan en los diccionarios
            if (veh_id, destino_id) not in params_carga_transportada:
                raise KeyError(f"Falta la clave ({veh_id}, {destino_id}) en `params_carga_transportada`.")
            if (veh_pos, destino_id) not in matrix_distancias:
                raise KeyError(f"Falta la clave ({veh_pos}, {destino_id}) en `matrix_distancias`.")
            
            # Obtener la distancia y verificar que no sea cero
            distancia = matrix_distancias[(veh_pos, destino_id)]
            if distancia == 0:
                raise ZeroDivisionError(f"La distancia entre {veh_pos} y {destino_id} es 0.")
            
            # Calcular el indicador
            carga_transportada = params_carga_transportada[(veh_id, destino_id)]
            params_ind_trafico[(veh_id, destino_id)] = carga_transportada / distancia

    return params_ind_trafico

def actualizar_destinos(destinos: List[Any], carga_veh_destino: Dict[tuple, float], resultado: Dict[str, Any]) -> None:
    """
    Actualiza el inventario de los destinos con base en la carga entregada y el resultado del ruteo.

    Args:
        destinos (List[Any]): Lista de objetos destino.
        carga_veh_destino (Dict[tuple, float]): Diccionario con la carga asignada a cada vehículo-destino.
                                                Las claves son tuplas (vehículo_id, destino_id).
        resultado (Dict[str, Any]): Diccionario con los resultados del modelo de optimización,
                                    incluyendo el ruteo en 'Ruteo'.
    """
    ruteo = resultado.get("Ruteo", {})

    for destino in destinos:
        for asignacion, estado in ruteo.items():
            veh_id, dest_id = asignacion  # Desempaquetar la tupla (vehículo_id, destino_id)
            if destino.identif == dest_id and estado == 1:
                # Actualizar inventario del destino con la carga asignada
                carga_entregada = carga_veh_destino.get(asignacion, 0)
                destino.set_inventario(carga_entregada)
                
                # Mensaje para depuración
                print(f"Vehículo: {veh_id}, Destino: {dest_id}, Carga: {carga_entregada}, Inventario actualizado: {destino.inventario}")

def actualizar_vehiculos(vehiculos: List[Any], carga_veh_destino: Dict[tuple, float], resultado: Dict[str, Any]) -> None:
    """
    Actualiza la carga y la posicion de los vehículos con base en la carga entregada y el resultado del ruteo.

    Args:
        vehiculos (List[Any]): Lista de objetos vehiculo.
        carga_veh_destino (Dict[tuple, float]): Diccionario con la carga asignada a cada vehículo-destino.
                                                Las claves son tuplas (vehículo_id, destino_id).
        resultado (Dict[str, Any]): Diccionario con los resultados del modelo de optimización,
                                    incluyendo el ruteo en 'Ruteo'.
    """
    ruteo = resultado.get("Ruteo", {})

    for veh in vehiculos:
        for asignacion, estado in ruteo.items():
            veh_id, dest_id = asignacion  # Desempaquetar la tupla (vehículo_id, destino_id)
            if veh.identif == veh_id and estado == 1:
                # Actualizar la carga del vehiculo con la carga asignada
                carga_entregada = carga_veh_destino.get(asignacion, 0)
                carga_actual = veh.carga - carga_entregada
                # Si el vehiculo se queda sin carga regresa al origen y carga a maxima capacidad
                if carga_actual==0:
                    veh.set_carga(veh.capacidad)
                    veh.set_posicion(0)
                # # Si el vehiculo aun tiene carga la conserva en espera de una proxima asignacion desde el destino
                else:
                    veh.set_carga(carga_actual)
                    veh.set_posicion(dest_id)
                                
                # Mensaje para depuración
                print(f"Vehículo: {veh_id}, Destino: {dest_id}, Carga: {carga_entregada}, Carga en vehiculo actualizada: {veh.carga}, Posicion de vehiculo actualizada: {veh.posicion}")